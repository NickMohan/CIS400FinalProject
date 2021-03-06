# C:\Users\nbfen\Downloads\dataset_2021-05-02\storage\2021-04-22_Bitcoin

#CIS400 - Social Media and Data Mining Final Project

import twitter
from helperFuncs import *
import json
import pickle
import time
from datetime import datetime
from dateutil.parser import parse
import os
import pandas as pd
from nltk.corpus import stopwords, words
from nltk import *
#nltk.download('stopwords')
from nltk.classify import NaiveBayesClassifier as bayes
import nltk.classify as classy
import string
import spacy
from random import sample
from autocorrect import Speller
import emoji
from textblob import TextBlob
#import en_core_web_sm
#nlp = en_core_web_sm.load()

# CHANGE THIS TO CONFIGURE THE CODE TO THE PREFERRED DATE
DATE = "2021-04-26"
# CHANGE THIS TO THE DATE YOU WANT THE TRAINING SET TO BE BUILT FOR
TRAINING_DATE = "2021-04-27"
# WHEREVER YOUR PRICE DATA .CSVs ARE
CURRENCY_PATH = ""
# WHEREVER YOUR TWEET DATA IS
TWEET_PATH = "C:\\Users\\nbfen\\Downloads\\dataset_2021-05-02\\storage\\"
# SHORT VERSION OF CURRENCY (btc, eth, doge)
CURR_SHORT = "btc"
# NAME OF CURRENCY (Bitcoin, Ethereum, Dogecoin)
CURRENCY = 'Bitcoin'


## CLASSES ##
# C1 - > 1%
# C2 - > .5%
# C3 - -.5% > x < .5%
# C4 - < -.5%
# C5 - < -1%

######################
## DATA PREPARATION ##
######################

# cleans/processes and categorizes price data for CURR_SHORT
def processPriceData():
    btc = pd.read_csv('{0}{1}.csv'.format(CURRENCY_PATH, CURR_SHORT))
    #btc['date'] = btc['time'].split(' ')[0]
    btc[['day','hour']] = btc.time.str.split(expand=True)
    btc['hour'] = btc.hour.str[:2]
    btc['hour'] = pd.to_numeric(btc.hour, errors="coerce")
    btc['change'] = ((btc['close'] - btc['open']) / btc['open']) * 100
    btc['C1'] = btc['change'] > 1
    btc['C2'] = btc['change'] > .5
    btc['C3'] = btc['change'].between(-.5,.5)
    btc['C4'] = btc['change'] < -.5
    btc['C5'] = btc['change'] < -1
    newbtc = btc[['day','hour','volume','change','C1','C2','C3','C4','C5']]
    print(newbtc)
    #newbtc.to_csv('newbtc.csv',index=None)
    return newbtc

# builds and returns a set of the top 2000 tokens for DATE
def makeTokenFeatureSet():
    print('CREATING TOKEN FEATURE SET...\n')
    total = []
    for i in range(24):
        print('Tokenizing hour ' + str(i) + ':\n')
        total.extend(tokenFeaturesHour(DATE,i))
        print('Done\n')
    tdist = FreqDist(total)
    token_features = [w for (w, c) in tdist.most_common(500)]
    print('TOKEN FEATURE SET COMPLETED\n')
    return token_features

# some helpful stuff we need to load in for tokenization
stop_words = set(stopwords.words('english')) 
nlp = spacy.load("en_core_web_sm")

# tokenizes the set day and hour and returns a list of all the tokens
# should be used for the purpose of generating a feature set as it does
# not tokenize tweets individually
def tokenFeaturesHour(day,hour):
    tw = pd.read_pickle('{2}{0}_{3}\\{0}_{1}_{3}_tweets.p'.format(day,hour,TWEET_PATH, CURRENCY))
    daystweets = []

    # helpful print statements for figuring out when the pickle file is broken
    #print(tw)
    #print(len(tw))
    #print(tw)
    #print(tw[0])
    for i in range(len(tw)):
        #print(tw[i][2])
        # grabs tweet text
        daystweets.append(tw[i][2])
        
    tokens = []
    
    # tokenize tweets
    for t in daystweets:
        tt = TweetTokenizer(t)
        tokens.extend(tt.tokenize(t))

    # remove stopwords and punctuation
    #filtered_tokens = []
    #for token in tokens:
    #    if token.lower() not in stop_words and token.lower() not in string.punctuation:
    #        filtered_tokens.append(token)
    #document = nlp(' '.join(filtered_tokens))

    filtered_tokens = []
    # temp_tokens = []
    word = set(words.words())
    spell = Speller(fast=True)

    for token in tokens:
        #removing hyperlinks
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        #token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if token.lower() not in stop_words and token.lower() not in string.punctuation:
            # temp_tokens.append(token)
            #filtered_tokens.append(token)

            if len(token) >2:
                if token.startswith('@'):
                    filtered_tokens.append(token)
                elif token.startswith('#'):
                    filtered_tokens.append(token)
                elif token.lower() in word:
                    filtered_tokens.append(token)
                elif token in emoji.UNICODE_EMOJI_ENGLISH:
                    filtered_tokens.append(token)
                elif (spell(token)) in word:
                    filtered_tokens.append(spell(token))
    document = nlp(' '.join(filtered_tokens))
    # remove named entities
    text_no_namedentities = []
    ents = [e.text for e in document.ents]
    for item in document:
        if item.text in ents:
            pass
        else:
            text_no_namedentities.append(item.text)
    return text_no_namedentities
    
    # remove named entities
    # text_no_namedentities = []
    # ents = [e.text for e in document.ents]
    # for item in document:
    #     if item.text in ents:
    #         pass
    #     else:
    #         text_no_namedentities.append(item.text)
    # return text_no_namedentities


###########################
## TRAINING SET CREATION ##
###########################

## VARIABLES ##
# change in the prior hour [C1 .. C5]
# tweet volume in the hour (0+,3k+,5k+)
# pos/neg classifier
# retweets (0+,10+,50+)
# contains emoji
# contains repeated emoji
# trading vol in the previous hour
# influencer tagged
# special influencer tagged

newbtc = processPriceData()
def prepHour(day,hour):
    tw = pd.read_pickle('{2}{0}_{3}\\{0}_{1}_{3}_tweets.p'.format(day,hour,TWEET_PATH, CURRENCY))
    #print(len(tw))
    compiled_hour = []

    print('Beginning price/volume categorization...')
    ## GET PREVIOUS DAYS CHANGE/VOLUME AND CATEGORIZE ##
    # pcFeat - category of previous hour's change [C1 ... C5]
    # vFeat - category of previous hour's volume [high = > 1k, medium = > 500, low = >0]
    pcFeat = "C3"
    vFeat = "low"
    chCategory = "C3"
    dayEntries = newbtc.loc[(newbtc['day'] == day)].reset_index()
    chChange = dayEntries.at[int(hour), 'change']
    try:
        if (hour == "0"):
            prevChange = newbtc.at[int(dayEntries.at[0,'index']) - 1, 'change']
            prevVol = newbtc.at[int(dayEntries.at[0,'volume']) - 1, 'change']
        else :
            prevChange = dayEntries.at[int(hour) - 1, 'change']
            prevVol = dayEntries.at[int(hour) - 1, 'volume']
    except:
        prevChange = 0
        prevVol = dayEntries.at[int(hour), 'volume']

    # print(prevChange)
    # print(prevVol)

    ## CATEGORIZE PREVIOUS HOUR CHANGE ##
    if(prevChange > 1):
        pcFeat = "C1"
    elif(prevChange > .5):
        pcFeat = "C2"
    elif(prevChange < -.5):
        pcFeat = "C4"
    elif(prevChange < -1):
        pcFeat = "C5"

    ## CATEGORIZE CURRENT HOUR CHANGE ##
    # used for training purposes
    # NOT a feature used in the trainingset
    if(chChange > 1):
        chCategory = "C1"
    elif(chChange > .5):
        chCategory = "C2"
    elif(chChange < -.5):
        chCategory = "C4"
    elif(chChange < -1):
        chCategory = "C5"

    ## CATEGORIZE VOLUME LEVEL ##
    if(prevVol > 1000):
        vFeat = "high"
    elif(prevVol > 500):
        vFeat = "medium"
    print('Done.')

    print('Beginning tweet-level parsing...')

    for i in range(len(tw)):
        features = {}
        features['phChange'] = pcFeat
        features['phVolume'] = vFeat

        text = tw[i][2]
        rts = tw[i][4]

        ## CATEGORIZE RETWEET LEVEL ##
        rtFeat = "low"
        if(rts > 50):
            rtFeat = "high"
        elif(rts > 10):
            rtFeat = "medium"
        
        features['rts'] = rtFeat

        # parse additional token-based features
        features = compileTweetTokenFeats(text, features)

        # add fully compiled feature set for tweet to day's accumulator
        compiled_hour.append((features,chCategory))
        
    print('Done.')
    return compiled_hour

# compile token-based features for the given tweet t, and 
# add it to the current feature set (features)
tFeats = makeTokenFeatureSet()
def compileTweetTokenFeats(t, f):
    features = f
    tt = TweetTokenizer(t)
    tokens = tt.tokenize(t)

    # remove stopwords and punctuation
    # filtered_tokens = []
    # for token in tokens:
    #     if token.lower() not in stop_words and token.lower() not in string.punctuation:
    #         filtered_tokens.append(token)
    # document = nlp(' '.join(filtered_tokens))
    # text_no_namedentities = []

    # # remove named entities
    # ents = [e.text for e in document.ents]
    # for item in document:
    #     if item.text in ents:
    #         pass
    #     else:
    #         text_no_namedentities.append(item.text)

    # remove stopwords and punctuation
    filtered_tokens = []
    # temp_tokens = []
    word = set(words.words())
    spell = Speller(fast=True)

    emojiFeat = False
    multEmojiFeat = False
    tagFeat = False
    elonTag = False

    for token in tokens:
        #removing hyperlinks
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        #token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if token.lower() not in stop_words and token.lower() not in string.punctuation:
            # temp_tokens.append(token)
            #filtered_tokens.append(token)
            if token.lower() == '@elonmusk':
                elonTag = True
            if len(token) >2:
                if token.startswith('@'):
                    filtered_tokens.append(token)
                    tagFeat = True
                elif token.startswith('#'):
                    filtered_tokens.append(token)
                elif token.lower() in word:
                    filtered_tokens.append(token)
                elif token in emoji.UNICODE_EMOJI_ENGLISH:
                    filtered_tokens.append(token)
                    if emojiFeat:
                        multEmojiFeat = True
                    else:
                        emojiFeat = True
                elif (spell(token)) in word:
                    filtered_tokens.append(spell(token))

    
        
    document = nlp(' '.join(filtered_tokens))
    text_no_namedentities = []
    # remove named entities
    ents = [e.text for e in document.ents]
    for item in document:
        if item.text in ents:
            pass
        else:
            text_no_namedentities.append(item.text)

    sent = "neutral"
    sentiFeat = 0
    for t in text_no_namedentities:
        temp = TextBlob(t)
        pol = temp.sentiment.polarity
        if (pol < -.3):
            sentiFeat -= 1
        elif (pol > .3):
            sentiFeat += 1
    if(sentiFeat > 3):
        sent = "positive"
    elif(sentiFeat < -3):
        sent = "negative"


    # todo - further tokenization

    features = document_features(text_no_namedentities, features)
    features['emojiHere'] = emojiFeat
    features['multEmojiHere'] = multEmojiFeat
    features['tagsHere'] = tagFeat
    features['elonTagHere'] = elonTag
    features['tweetSentiment'] = sent

    # todo - fill in other token based features
    # pos/neg classifier
    # contains emoji
    # contains repeated emoji
    # influencer tagged
    # special influencer tagged (like elon)
    
    return features

# gather the token-based features for the given tweet
# token-based features are based on the result of our makeTokenSet() function
def document_features(tweet, f): # tweet is list of tokens
    features = f
    document_words = set(tweet)
    for word in tFeats:
        a = 1+1
        features['contains(%s)' % word] = (word in document_words)
    return features    

# prepare and return the training set for TRAINING_DATE
def prepDay():
    day_compiled = []
    print('BEGINNING CREATION OF TRAINING SET FOR ' + TRAINING_DATE + '\n')
    for i in range(24):
        print('BEGINNING HOUR ' + str(i) + '...')
        day_compiled.extend(prepHour(TRAINING_DATE,str(i)))
        print('COMPLETED HOUR ' + str(i) + '\n')
    print('TRAINING SET CREATION COMPLETED')

    new_dict = defaultdict(list)

    #csv file generator
    for i in day_compiled:
        keyVals = []
        for key in i[0].keys():
            keyVals.append(i[0][key])
        for val,x in zip(keyVals,i[0].keys()):
            new_dict[x].append(val)
        keyVals.append(i[1])
        cat = len(keyVals) - 1
        new_dict['category'].append(keyVals[cat])
    df = pd.DataFrame(new_dict)
    df.to_csv(CURRENCY + '-' + TRAINING_DATE + '.csv',index=False, header=True)
    

    return day_compiled

# prepHour(TRAINING_DATE,"0")

##########################
## BAYES CLASSIFICATION ##
##########################

# I don't know if this works yet with the current format of the training set
def training():
    full_set = prepDay()
    print('Sampling training set...\n')
    sample_set = sample(full_set,10000)
    train_set, test_set = sample_set[5000:], sample_set[:5000]
    print('Training...\n')
    classifier = bayes.train(train_set)
    print('Accuracy:')
    print(classy.accuracy(classifier, test_set))
    print(classifier.show_most_informative_features(200))

training()

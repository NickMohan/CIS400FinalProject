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
from nltk.corpus import stopwords 
from nltk import *
import string
import spacy
#import en_core_web_sm
#nlp = en_core_web_sm.load()

# CHANGE THIS TO CONFIGURE THE CODE TO THE PREFERRED DATE
DATE = "2021-04-26"
# WHEREVER YOUR PRICE DATA .CSVs ARE
CURRENCY_PATH = ""
# WHEREVER YOUR TWEET DATA IS
TWEET_PATH = "C:\\Users\\nbfen\\Downloads\\dataset_2021-05-02\\storage\\"
# SHORT VERSION OF CURRENCY (btc, eth, doge)
CURR_SHORT = "btc"
# NAME OF CURRENCY (Bitcoin, Ethereum, Dogecoin)
CURRENCY = 'Bitcoin'

# some code to load in the price 
# also categorizes pos/neg price changes by hour
btc = pd.read_csv('{0}{1}.csv'.format(CURRENCY_PATH, CURR_SHORT))
btc['today'] = list(
    map(lambda x: x.startswith(DATE), btc['time']))
btc = btc[btc['today'] == True]
print(btc)
btc['change'] = ((btc['close'] - btc['open']) / btc['open']) * 100
print(btc['change'])
btc['fall'] = btc['change'] < -.5
btc['rise'] = btc['change'] > .5
btc = btc.reset_index()
print(btc)


# returns the tokens for a given day and time
# time must be entered as 'YYYY-MM-DD' and time as 0-23
# tokens are free of most punctunation, stopwords, and named entities
def getTokens(day,time):
    tw = pd.read_pickle('{2}{0}_{3}\\{0}_{1}_{3}_tweets.p'.format(day,time,TWEET_PATH, CURRENCY))
    daystweets = []
    rts = []
    # helpful print statements for figuring out when the pickle file is broken
    #print(tw)
    #print(len(tw))
    #print(tw)
    #print(tw[0])
    for i in range(len(tw)):
        #print(tw[i][2])
        # grabs tweet text
        daystweets.append(tw[i][2])
        # grabs retweet count [NOT USED OR RETURNED YET, BUT SHOULD BE]
        rts.append(tw[i][4])

    tokens = []
    stop_words = set(stopwords.words('english')) 
    nlp = spacy.load("en_core_web_sm")

    # tokenize tweets
    for t in daystweets:
        tt = TweetTokenizer(t)
        tokens.extend(tt.tokenize(t))

    # remove stopwords and punctuation
    filtered_tokens = []
    for token in tokens:
        if token.lower() not in stop_words and token.lower() not in string.punctuation:
            filtered_tokens.append(token)
    document = nlp(' '.join(filtered_tokens))
    text_no_namedentities = []
    # remove named entities
    ents = [e.text for e in document.ents]
    for item in document:
        if item.text in ents:
            pass
        else:
            text_no_namedentities.append(item.text)
    return text_no_namedentities

# returns two lists, representing the 2000 most common tokens (and their associated frequencies) 
# for the positive/negative price hours -- pos/neg defined as +/- .5% price change
def getDaysPosNeg():
    postotal = []
    negtotal = []

    print("Tokenizing Hourly Tweets For " + CURRENCY + ":\n")
    for i in range(24):
        date = DATE
        time = str(i)
        print('Determining price change category for ' + time + "\n")

        # checks to see if hour belongs to a significant pos/neg price change (> |+/-.5%|)
        if(btc.at[i, 'rise'] == True):
            print('Hour ' + time + ' was a price rise, tokenizing...\n')
            postotal.extend(getTokens(date,time))
        if(btc.at[i, 'fall'] == True):
            print('Hour ' + time + ' was a price fall, tokenizing...\n')
            negtotal.extend(getTokens(date,time))
        print('Done tokenzing.\n')
        

    # creates frequency distribution for pos/neg price change hours
    pdist = FreqDist(postotal)
    pos_word_features = [w for (w, c) in pdist.most_common(2000)]
    ndist = FreqDist(negtotal)
    neg_word_features = [w for (w, c) in ndist.most_common(2000)]

    print('Price Increase Tokens (top 10 percent of collected sample):')
    print(pdist.most_common(200))
    print('\n')
    print('Tags to Elon During Price Increases: ')
    print(pdist['@elonmusk'])
    print('\n')
    print('Moon References During Price Increases: ')
    print(pdist['moon'])
    print('\n\n')
    print('Price Fall Tokens (top 10 percent of collected sample):')
    print(ndist.most_common(200))
    print('\n')
    print('Tags to Elon During Price Falls: ')
    print(ndist['@elonmusk'])
    print('\n')
    print('Moon References During Price Falls: ')
    print(ndist['moon'])
    print('\n\n')
    
    return pos_word_features, neg_word_features

def extract_features(document): # I renamed it
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

getDaysPosNeg()

# START MAKING TRAINING SET HERE
# FEATURES TO BE ADDED:
#retweet density
#tweet volume
#avg sentiment for hour
#bitcoin/etherum volume
#bucketed influences
#density of people tagging influencers
#important emoji density


#fdist = FreqDist(total)
#word_features = [w for (w, c) in fdist.most_common(2000)]
#print(fdist.most_common(100))
#print(fdist['@elonmusk'])

#training_set = classify.apply_features(extract_features, tweets)


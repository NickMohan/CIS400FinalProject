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
#nltk.download('stopwords')
from nltk.classify import NaiveBayesClassifier as bayes
import nltk.classify as classy
import string
import spacy
from random import sample
#import en_core_web_sm
#nlp = en_core_web_sm.load()

# CHANGE THIS TO CONFIGURE THE CODE TO THE PREFERRED DATE
DATE = "2021-04-22"
# CHANGE THIS TO THE DATE YOU WANT THE TRAINING SET TO BE BUILT FOR
TRAINING_DATE = "2021-04-26"
# WHEREVER YOUR PRICE DATA .CSVs ARE
CURRENCY_PATH = ""
# WHEREVER YOUR TWEET DATA IS
TWEET_PATH = "C:\\Users\\nbfen\\Downloads\\dataset_2021-05-02\\storage\\"
# SHORT VERSION OF CURRENCY (btc, eth, doge)
CURR_SHORT = "btc"
# NAME OF CURRENCY (Bitcoin, Ethereum, Dogecoin)
CURRENCY = 'Bitcoin'

def getCurrencyData(day):
    btc = pd.read_csv('{0}{1}.csv'.format(CURRENCY_PATH, CURR_SHORT))
    btc['today'] = list(
        map(lambda x: x.startswith(day), btc['time']))
    btc = btc[btc['today'] == True]
    print(btc)
    btc['change'] = ((btc['close'] - btc['open']) / btc['open']) * 100
    print(btc['change'])
    btc['fall'] = btc['change'] < -.5
    btc['rise'] = btc['change'] > .5
    btc = btc.reset_index()
    print(btc)
    return btc

def getTopTokens(day):
    total = []
    for i in range(24):
        print('Tokenizing hour ' + str(i) + ':\n')
        total.extend(getTokens(day,i))
        print('Done\n')
    tdist = FreqDist(total)
    word_features = [w for (w, c) in tdist.most_common(2000)]
    return word_features

def getTokens(day,time):
    tw = pd.read_pickle('{2}{0}_{3}\\{0}_{1}_{3}_tweets.p'.format(day,time,TWEET_PATH, CURRENCY))
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

print('Building Main Feature Set:\n')
tweet_features = getTopTokens(DATE)
print('Done Building Main Feature Set\n')
def document_features(tweet): # tweet is list of tokens
    document_words = set(tweet)
    features = {}
    for word in tweet_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

def prepHour(day,time):
    btc = getCurrencyData(day)
    tw = pd.read_pickle('{2}{0}_{3}\\{0}_{1}_{3}_tweets.p'.format(day,time,TWEET_PATH, CURRENCY))
    tweets = []
    stop_words = set(stopwords.words('english')) 
    nlp = spacy.load("en_core_web_sm")
    # helpful print statements for figuring out when the pickle file is broken
    #print(tw)
    #print(len(tw))
    #print(tw)
    #print(tw[0])
    print('Prepping Hour ' + str(time) + '...')
    for i in range(len(tw)):
        #print(tw[i][2])
        # grabs tweet text
        t = tw[i][2]
        
        tt = TweetTokenizer(t)
        tokens = tt.tokenize(t)
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
        tweets.append(text_no_namedentities)
    print('Done tokenizing...')


    if(btc.at[time, 'rise'] == True):
        featuresets = [(document_features(t), 'rise') for t in tweets]
        print('Done categorizing....Finished.\n')
        return featuresets
    if(btc.at[time, 'fall'] == True):
        featuresets = [(document_features(t), 'fall') for t in tweets]
        print('Done categorizing....Finished.\n')
        return featuresets
    print('Done categorizing....Finished.\n')
    return []

def prepDay(day):
    print('Starting Training Set Prep:\n')
    final = []
    for i in range(24):
        temp = prepHour(day,i)
        if (temp != []):
            final.extend(temp)
        print('Added to Training Set. Ready For Next Hour. \n')
    return final


full_set = prepDay(TRAINING_DATE)
print('Sampling training set...\n')
sample_set = sample(full_set,200)
train_set, test_set = sample_set[100:], sample_set[:100]
print('Training...\n')
classifier = bayes.train(train_set)
print('Accuracy:')
print(classy.accuracy(classifier, test_set))
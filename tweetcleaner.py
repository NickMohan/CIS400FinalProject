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

BASE_PATH = 'C:\\Users\\nbfen\\Downloads\\dataset_2021-05-02\\storage'

btc = pd.read_csv('btc.csv')
today = '2021-04-22'
#print(btc.head(10))
btc['today'] = list(
    map(lambda x: x.startswith(today), btc['time']))
btc = btc[btc['today'] == True]
print(btc)
btc['change'] = ((btc['close'] - btc['open']) / btc['open']) * 100
print(btc['change'])
btc['fall'] = btc['change'] < -.5
btc['rise'] = btc['change'] > .5
btc = btc.reset_index()
print(btc)



def getTokens(day,time):
    tw = pd.read_pickle('storage\\{0}_Bitcoin\\{0}_{1}_Bitcoin_tweets.p'.format(day,time))
    daystweets = []
    rts = []
    #print(len(tw))
    for i in range(len(tw)):
        daystweets.append(tw[i][2])
        rts.append(tw[i][4])

    tokens = []
    stop_words = set(stopwords.words('english')) 
    nlp = spacy.load("en_core_web_sm")


    for t in daystweets:
        tt = TweetTokenizer(t)
        tokens.extend(tt.tokenize(t))

    filtered_tokens = []
    for token in tokens:
        if token.lower() not in stop_words and token.lower() not in string.punctuation:
            filtered_tokens.append(token)
    document = nlp(' '.join(filtered_tokens))
    text_no_namedentities = []

    ents = [e.text for e in document.ents]
    for item in document:
        if item.text in ents:
            pass
        else:
            text_no_namedentities.append(item.text)
    return text_no_namedentities

postotal = []
negtotal = []
for i in range(24):
    date = "2021-04-22"
    time = str(i)
    print(btc.at[i, 'rise'])

    if(btc.at[i, 'rise'] == True):
        postotal.extend(getTokens(date,time))
    #r = getTokens(date,time)
        
    if(btc.at[i, 'fall'] == True):
        negtotal.extend(getTokens(date,time))
pdist = FreqDist(postotal)
pos_word_features = [w for (w, c) in pdist.most_common(2000)]
print(pdist.most_common(2000))
ndist = FreqDist(negtotal)
neg_word_features = [w for (w, c) in ndist.most_common(2000)]
print(ndist.most_common(2000))

print(pdist['@elonmusk'])
print(pdist['moon'])
print(ndist['@elonmusk'])
print(ndist['moon'])


def extract_features(document): # I renamed it
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features



#fdist = FreqDist(total)
#word_features = [w for (w, c) in fdist.most_common(2000)]
#print(fdist.most_common(100))
#print(fdist['@elonmusk'])

#training_set = classify.apply_features(extract_features, tweets)

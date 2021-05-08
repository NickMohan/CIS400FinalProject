import requests
import pickle
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import pandas as pd


def getCleanTokensForHour(day,time):
    #Load tweets
    tw = pd.read_pickle('storage/{0}_Bitcoin/{0}_{1}_Bitcoin_tweets.p'.format(day,time))
    daystweets = []
    rts = []

    #Tweet Volume of the hour
    #print(len(tw))

    #Get tweets text and retweet amounts
    for i in range(len(tw)):
        daystweets.append(tw[i][2])
        rts.append(tw[i][4])

    return daystweets, rts


if __name__ == "__main__":

    text, _ = getCleanTokensForHour("2021-04-25","23")

    #Sentiment140
    formatList = []
    for t in text:
        formatList.append({"text":t})
    postBody = {"data":formatList}
    r = requests.post("http://www.sentiment140.com/api/bulkClassifyJson?appid=njmohan@syr.edu", json=postBody)
    returnTweets = r.json()['data']
    senti = [0,0,0]
    for x in returnTweets:
        if (x["polarity"] == 4):
            senti[0] += 1
        elif (x["polarity"] == 2):
            senti[1] += 1
        else:
            senti[2] += 1

    print("sentiment 140")
    print("pos","neutral","neg")
    print(senti)

    #nltk VADER
    classifier = SentimentIntensityAnalyzer()
    senti = [0,0,0]
    for t in text:
        temp = classifier.polarity_scores(t)
        comp = float(temp['compound'])
        if(comp < -0.3):
            senti[2] += 1
        elif(comp < 0.3):
            senti[1] += 1
        else:
            senti[0] += 1

    print("\nVader")
    print("pos","neutral","neg")
    print(senti)

    #Textblob
    senti = [0,0,0]
    subjective = 0
    for t in text:
        temp = TextBlob(t);
        pol = temp.sentiment.polarity
        if(pol < -0.3):
            senti[2] += 1
        elif(pol < 0.3):
            senti[1] += 1
        else:
            senti[0] += 1
        sub = temp.sentiment.subjectivity
        if(sub > 0.5):
            subjective += 1
    print("\nText Blob")
    print("pos","neutral","neg")
    print(senti)
    print("Subjective:", subjective)


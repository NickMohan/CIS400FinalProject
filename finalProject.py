#CIS400 - Social Media and Data Mining Final Project

import twitter
from helperFuncs import *
import json
import pickle
import time
from datetime import datetime
from dateutil.parser import parse
import os

#Returns tweets for the day before the date entered
def getAllTweetsOnDay(twitter_api, query, date):
    tweetDict = {}

    #Only want to get tweets for current day
    #and twitter only has max time parameter
    #so we have to keep track on the min time
    #ourselves
    pastDate = False

    #Store tweet volume
    tweetVolume = 0
    retweetVolume = 0


    #Get what hour of the day we are scrapping tweets for
    #mainly for storage of the tweet data for later use
    currentHour = 0

    #Get the intial response from the twitter API
    response = make_twitter_request(twitter_api.search.tweets, q=query, result_type='recent', count='100', until=date)


    #If the response is not empty set the current hour we start scraping at and
    #make the folder to store this days data in for the specific query we are using
    if(len(response['statuses']) != 0):
        currentHour = parse(response['statuses'][0]['created_at']).hour
        if not os.path.exists('storage/'+date+"_"+query):
            os.makedirs('storage/'+date+"_"+query)

    #While we are not out of tweets for the query or are still on the approiate day
    while(len(response['statuses']) != 0 and not pastDate):
        #Go through each of the tweet objects one by one
        for tweet in response['statuses']:
            #Check if retweet, if it is a retweet, add it to the retweet count
            #If it is not a retweet add it to reagular count and store the tweet
            if 'retweeted_status' in tweet:
                retweetVolume = retweetVolume + 1
            else:
                #Check what day we are scraping tweets for, if it is not the correct day stop the function
                tweetDate = parse(tweet['created_at'])
                if(tweetDate.day != (int(date[8:10])-1)):
                    pastDate = True
                    break
                #If we enter a new hour, dump the previous hour tweets into a pickle object and start a new dictionary
                if(tweetDate.hour != currentHour):
                    fileName = 'storage/'+date+"_"+query+"/"+date+"_"+str(currentHour)+"_"+query+"_tweets.p"
                    with open(fileName, 'wb') as f:
                        pickle.dump(tweetDict, f, protocol=pickle.HIGHEST_PROTOCOL)
                    tweetDict = {}
                    currentHour = tweetDate.hour


                #Add the tweet data to the dictionary which will get pickled. Can change for what metadata we want
                #the below attributes being stored is the bare min that we will need
                tweetData = [tweet['user']['screen_name'], tweet['created_at'], tweet['text'], tweet['id']]
                tweetDict[tweetVolume] = tweetData
                tweetVolume = tweetVolume + 1

        #After every bath of tweets print out an update with the current time, the time of the tweets we are scraping, as well as
        #Other information so we know the program is not stalled
        print("Current Time: ",time.ctime(),"\nTime Of Day Tweets: ", response['statuses'][0]['created_at'],"\nTweetVolume: ", tweetVolume, "\nReTweetVolume: ", retweetVolume)

        #Get the lastID from the previous batch and then subtract one and make that the max_id of the next batch so we continue getting
        #new tweets
        lastID = response['statuses'][len(response['statuses'])-1]['id']
        response = make_twitter_request(twitter_api.search.tweets, q=query, result_type='recent', count='100', until=date, max_id = lastID-1)


    #Pickle file for storing the tweets
    fileName = 'storage/'+date+"_"+query+"/"+date+"_"+str(currentHour)+"_"+query+"_tweets.p"
    with open(fileName, 'wb') as f:
        pickle.dump(tweetDict, f, protocol=pickle.HIGHEST_PROTOCOL)

    #Print out the total tweet volume as well as the retweet volume just so we can see it
    print(tweetVolume)
    print(retweetVolume)


#Quick function for reading data from a pickle file will make this more
#robust and user friendly in the future
def readTweetsFromStorage(fileName):
        with open(fileName, 'rb') as f:
            tweets = pickle.load(f)
        for data in tweets:
            print(data, tweets[data])



#I think it may be helpful for adding another parameter for a max_id for the first tweet so that
#if the program stalls we can start off where we last saved data in the pickle file and not have
#rerun the entire program
if __name__ == "__main__":
    twitter_api = oauth_login()

    #Right now just scrapping data for one day, will modify this to get the rest of the data as needed
    q = "Dogecoin"
    date = "2021-04-20"
    getAllTweetsOnDay(twitter_api, q, date)

    #Used for reading the data, just change date and hour
    #I plan on developing a better system for reading the tweet data later on so we can spot check data
    #readTweetsFromStorage('storage/2021-04-20_Dogecoin/2021-04-20_23_Dogecoin_tweets.p')




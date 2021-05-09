import pickle
import os


crypto = ["Bitcoin", "Dogecoin", "Ethereum"]

if __name__ == "__main__":
    #Go through each crypto
    for name in crypto:
        #Open file for storing volume data for that crypto
        f = open("storage/volumeData"+name+".txt", "w")
        #Open storage folder and find all of the data we need
        for root,dirs,files in os.walk("storage"):
            #If this file pack is the right size, andis the current crypto we are searching for
            if(len(files) == 24 and name in files[0]):
                #Every file open it and count number of tweets then record in file
                for fileName in files:
                    with open(root + "/" + fileName, 'rb') as k:
                        tweets = pickle.load(k)
                    temp = fileName[:-9]+"\t"+str(len(tweets))+"\n"
                    f.write(temp)
        f.close()

# CIS400FinalProject
CIS400 Social Media and Data Mining FinalProject

# Main Files
bayesV4.py - Final Build of the Bayes Naive Classifier

tweetCollection.py - Tweet Data Collector

pricegrabba.py - Price Data Collector

crypto.zip - Compiled Price Data

dataset_2021-05-02.zip - Compiled Tweet Data

requirements.txt - Dependency Information

# Setup
This project is tested using python version 3.9

To setup the project you first need to install all of the project dependencies. A requirements.txt file is included. This
can be used to install the required dependencies for this project.

Then you need to supply Twitter keys into the program. For security all twitter keys
are offline with the owner of the keys and off of the Github repo. To add Twitter keys to the project the user
first should create a file in the main directory called config.py. Then the user should copy the following
format into the config file. Afterwards the user shall fill in the appropriate keys in the config file and
save it. Once is do the user is ready to run the project.

### config.py file outline
apiKey = 'KEY HERE'

apiSecret = 'KEY HERE'

oauthKey = 'KEY HERE'

oauthSecret = 'KEY HERE'


#Running The Project: Tweet Collection
To start the project the user first needs to collect tweets to create a dataset. The user should run the tweetCollection.py using the command:

python3 tweetCollection.py

This program will run getting all of the tweet data for the three cryptocurrencies for the past week. This data will be stored in a storage file
called storage. Once this program is done running the user can go ahead and run the second part of this project.

#Running The Project: Tweet Cleaning And Prediction Creation
The final build of Bayes is configured to run a 5k-entry training/test set from a given date. You will need to download the bayesV4.py file alongside the two zip files containing the price/tweet data. Once this is done, the 6 global variables are all you should need to fill out for this code to work (so long as imported dependencies are installed). Specific instructions are given in the file, but these allow you to set the location of your compiled data, the currency you want to analyze, and the date you want to analyze.



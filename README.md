# CIS400FinalProject
CIS400 Social Media and Data Mining FinalProject

# Main Files
bayesV4.py - Final Build of the Bayes Naive Classifier

finalProject.py - Tweet Data Collector

pricegrabba.py - Price Data Collector

crypto.zip - Compiled Price Data

dataset_2021-05-02.zip - Compiled Tweet Data

# How to Run The Final Bayes Build
The final build of Bayes is configured to run a 5k-entry training/test set from a given date. You will need to download the bayesV4.py file alongside the two zip files containing the price/tweet data. Once this is done, the 6 global variables are all you should need to fill out for this code to work (so long as imported dependecies are installed). Specific instructions are given in the file, but these allow you to set the location of your compiled data, the currency you want to analyze, and the date you want to analyze.

# Setup
To setup the project you first need to run the requirements.txt file to install all of the
dependencies for the project. This file will be done soon. I have not gotten to it yet

Also what needs to be done is to either put your twitter api keys into the helperFuncs.py file,
or you need to create a config.py file and copy in the text from below and put your keys in there.
The config file is hidden in the .gitignore so no twitter api keys will be made public.

Also you need to create a folder called storage in the root directory of the project. This is where
the tweet data will be stored

### config.py file outline
apiKey = 'KEY HERE'

apiSecret = 'KEY HERE'

oauthKey = 'KEY HERE'

oauthSecret = 'KEY HERE'


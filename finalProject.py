#CIS400 - Social Media and Data Mining Final Project

import twitter
from helperCookbook import *


screenNameOriginal = "kanyewest"

if __name__ == "__main__":

    twitter_api = oauth_login()
    response = make_twitter_request(twitter_api.users.lookup,screen_name=screenNameOriginal)

    print(response)



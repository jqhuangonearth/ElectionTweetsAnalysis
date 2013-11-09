#!/usr/bin/env python
# -*- coding: utf-8  -*-
#encoding=utf-8

import tweepy
import time
import sys
from random import randint
#from utils import TimeOutAlarm

#sys.setdefaultencoding('utf-8')
#F = codecs.open('try.txt','w', 'utf-8')

class TwitterCrawler():
    consumer_key = "K5ght1jy6fI1w8mpUCeiQ"
    consumer_secret = "TdXtIb5upWPuLoFAJFWjalhmIgqcoZLNvw1IaTWTGS4"
    access_key = "1260900631-3N7q5aSs9FgJxC3gwML0aRkQWiB4bTxuXzUYvjI"
    access_secret = "x0DsZIvOX08AIwPLev4KyphulqI9n7HphlT0BDnYI"
    auth = None
    api = None
    #time_out_alarm = TimeOutAlarm() 

    def __init__(self):
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_key, self.access_secret)
        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())
        #print self.api.rate_limit_status()

    def re_init(self):
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_key, self.access_secret)
        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())

    def check_api_rate_limit(self, sleep_time):
        #while self.api.rate_limit_status()['remaining_hits'] < 500:
        try:
            rate_limit_status = self.api.rate_limit_status()
        except Exception as error_message:
            if error_message['code'] == 88:
                print "Sleeping for %d seconds." %(sleep_time)
                print rate_limit_status['resources']['statuses']
                time.sleep(sleep_time)

        while rate_limit_status['resources']['statuses']['/statuses/user_timeline']['remaining'] < 10:
            print "Sleeping for %d seconds." %(sleep_time)
            print rate_limit_status['resources']['statuses']
            time.sleep(sleep_time)
            rate_limit_status = self.api.rate_limit_status()
        print rate_limit_status['resources']['statuses']['/statuses/user_timeline']

    def crawl_user_profile(self, user_id):
        self.check_api_rate_limit(900)
        #self.time_out_alarm.set_time_out_alarm(10)
        try:
            user_profile = self.api.get_user(user_id)
        except:
            return None
        return user_profile
    # added: crawl the friendslist and follwers list of tweeter given ids
    def crawl_user_friends_followers(self, user_id):
        return 0

    def crawl_user_tweets(self, user_id, count):
        self.check_api_rate_limit(900)
        #self.time_out_alarm.set_time_out_alarm(10)
        try:
            tweets = self.api.user_timeline(user_id, count = count)
        except:
            tweets = None
        tried_count = 0
        while len(tweets) < count:
            #self.time_out_alarm.set_time_out_alarm(10)
            try:
                tweets.extend(self.api.user_timeline(user_id, count = count))
            except:
                pass
            tried_count += 1
            if tried_count == 3:
                break
        return tweets[:count]

def main():
    tc = TwitterCrawler()
    tc.check_api_rate_limit(900)
    #user = tc.crawl_user_profile(12)
    #tweets = tc.crawl_user_tweets(20, 500)
    #print len(tweets)

if __name__ == "__main__":
    main()

"""
@author: Bolun Huang
@description: get semantic score of selected topics from alchamy api
"""


import cjson
import json
import httplib2
import urllib
import re
from pymongo import Connection
import nltk
import time

class topic_semantic_check:
    
    def __init__(self):
        self.APIKEY = urllib.quote_plus('c8231ecbb8f6dbe91199d3318a6a604ac24e5da9')
        self.http = httplib2.Http()
        self.DBSERVER = "localhost"
        self.DBPORT = 27017
        self.DBNAME = "user_vector"
        self.COLLECTION = "user_vector"
        self.conn = Connection(self.DBSERVER, self.DBPORT)
        self.db = self.conn[self.DBNAME]
        self.user_vector = {}
        self.semantic_topics = ["tcot", "syria", "p2", "bengahazi", "obama",
                                "teaparty", "uniteblue", "gop", "obamacare",
                                "tlot", "pjnet", "lnyhbt", "tgdn", "israel",
                                "ccot", "romneyryan2012", "nra", "nsa", "irs"]
        
        self.features = ["statuses_count", "description", "friends_count", "created_at", 
                         "class", "followers_count", "screen_name", "tweets", 
                         "favourites_count", "listed_count", "id", "name"]

        
    def read_user_vector(self, filename):
        f = open(filename, "r")
        count = 0
        for line in f:
            data = cjson.decode(line)
            self.user_vector.update({data["screen_name"] : {"_id" : count}}) # add default _id
            self.user_vector.update({data["screen_name"] : {key : data[key] for key in self.features}})
            count += 1
        f.close()
        
    """
    process the sentence and return a list of lower case words/terms
    remove stopwords; remove url, '\'w'.
    """
    def process_sentence(self, text):
        text1 = ""
        try:
            # to lower case
            text1 = text.lower()
            # remove url
            text1 = re.sub(r'http:[\\/.a-z0-9]+\s?', '', text1)
            text1 = re.sub(r'https:[\\/.a-z0-9]+\s?', '', text1)
            # rmove mentioned user names
            text1 = re.sub(r'(@\w+\s?)|(@\s+)', '', text1) 
            # remove special characters
            text1 = re.sub(r'[\#\-\+\*\`\.\;\:\"\?\<\>\[\]\{\}\|\~\_\=\!\^\&\(\)]', '', text1) 
            # remove retweet tag
            text1 = re.sub(r'rt\s?', '', text1)
        except:
            print text1
            pass
        try:
            text1 = nltk.word_tokenize(text1)
        except:
            text1 = []
            pass
        words = []
        for i in range(len(text1)):
            if "'" in text1[i] or text1[i] in nltk.corpus.stopwords.words('english'):
                pass
            else:
                words.append(text1[i])
        return words
    
    def send_query(self, text):
        query = 'http://access.alchemyapi.com/calls/text/TextGetTextSentiment?apikey={0}&text={1}&outputMode=json'.format(self.APIKEY, urllib.quote_plus(text.encode('utf8')))
        (header, context) = self.http.request(query, 'GET')
        if header and header['status'] == '200':
            result = cjson.decode(context)
            if result['status'] == 'OK':
                if result['docSentiment']['type'] == 'neutral':
                    #print "neutral"
                    return 0.0
                elif float(result['docSentiment']['score']) > 0.01 or float(result['docSentiment']['score']) < -0.01:
                    #print result['docSentiment']['score']
                    return float(result['docSentiment']['score'])
                else:
                    pass
            else:
                print "result error: ", result
                if result["statusInfo"] == 'daily-transaction-limit-exceeded':
                    print "need to sleep for 86399 sec"
                    time.sleep(86399)
                    
                    
                #error:  {'status': 'ERROR', 'statusInfo': 'daily-transaction-limit-exceeded'}
        else:
            print "header error: ", header
            pass
        return None
        
    def check(self):
        count = 0
        self.read_user_vector("user_vector/user_vector.json")
        self.user_list = self.get_user_list("data/labelled_user_new.txt")
        self.topic_list = self.get_topics()
        for user in self.user_vector:
            #user_semantics_topics = {self.semantic_topics[i] : 0.0 for i in range(len(self.semantic_topics))} # semantic dict
            #user_semantics_counts = {self.semantic_topics[i] : 0.0 for i in range(len(self.semantic_topics))} # semantic dict for count
            print "processing %s..." %user
            for i in range(len(self.user_vector[user]["tweets"])):
                tweet = self.user_vector[user]["tweets"][i]
                words = self.process_sentence(tweet["text"])
                score = self.send_query(" ".join(words))
                count += 1
                #print self.send_query(tweet["text"]), tweet["text"]
                tweet.update({"sentiment_score" : score})
                self.user_vector[user]["tweets"][i] = tweet
            print "done processing %s.. %d.." %(user, count)
        f = open("user_vector/user_vector_new.json","w")
        for user in self.user_vector:
            json.dump(self.user_vector[user], f)
        f.close()
            
    
    def get_user_list(self, filename):
        user_list = []
        f = open(filename, "r")
        for line in f:
            if not line.startswith("#"):
                line = line.split()
                user_list.append(line[0])
        f.close()
        return user_list
        
    def get_topics(self):
        return ["tcot", "syria", "p2", "bengahazi", "obama",
                "teaparty", "uniteblue", "gop", "obamacare",
                "tlot", "pjnet", "lnyhbt", "tgdn", "israel",
                "ccot", "romneyryan2012", "nra", "nsa", "irs"]
        
def main():
    mycheck = topic_semantic_check()
    mycheck.check()
    
if __name__ == "__main__":
    main()
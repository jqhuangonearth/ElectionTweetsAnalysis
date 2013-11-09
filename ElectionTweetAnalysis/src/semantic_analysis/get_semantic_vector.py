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
        self.f = open("user_vector/user_vector.json", "r")
        self.fo = open("user_vector/user_vector_new.json", "w")
        
    def check(self):
        self.user_list = self.get_user_list("data/labelled_user_new.txt")
        self.topic_list = self.get_topics()
        c = 1
        for line in self.f:
            user_semantics = {}
            data = cjson.decode(line)
            user = data['screen_name']
            for topic in self.topic_list:
                count = 0
                summation = 0.0
                tweets = data['tweets']
                for t in tweets:
                    if topic in t["text"]:
                        text = t["text"].lower()
                        text = re.sub(r'http:[\\/.a-z0-9]+\s?', '', text)
                        text = re.sub(r'(@\w+\s?)|(@\s+)', '', text)
                        text = re.sub(r'[#-+*]', '', text)
                        text = re.sub(r'rt\s?', '', text)
                        text = text.strip()
                        query = 'http://access.alchemyapi.com/calls/text/TextGetTextSentiment?apikey={0}&text={1}&outputMode=json'.format(self.APIKEY, urllib.quote_plus(text.encode('utf8')))
                        (header, context) = self.http.request(query, 'GET')
                        if header and header['status'] == '200':
                            result = cjson.decode(context)
                            if result['status'] == 'OK':
                                if result['docSentiment']['type'] == 'neutral':
                                    pass
                                elif float(result['docSentiment']['score']) > 0.01 or float(result['docSentiment']['score']) < -0.01:
                                    summation += float(result['docSentiment']['score'])
                                    count += 1
                                else:
                                    pass
                            else:
                                print "error: ", result
                        else:
                            print "error ", user
                            pass

                if count > 0:
                    user_semantics[topic] = summation/float(count)
                else:
                    user_semantics[topic] = 0.0
            print c, user
            c += 1
            data.update(user_semantics)
            json.dump(data, self.fo)
            self.fo.write('\n')
        self.fo.close()
        self.f.close()
    
    def get_user_list(self, filename):
        user_list = []
        f = open(filename, "r")
        for line in f:
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
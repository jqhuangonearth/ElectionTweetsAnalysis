"""
@description: this program automatically pick hashtags from the tweets and rank them
Among those hash tags, feed the tweets to the Alchami API and generate a distribution
of the sentiment score of each hashtag
By comparing the sentiment score distribution of each hashtag we apply feature selection
on hashtags and classify the same group of users using these new sentiment related
features.
@author: bolun
@date: Sep 16 2013
"""
import cjson

class hashtag():
    def __init__(self):
        self.hashtag_dic = {}
        self.hashtag_list = [] # list of hashtags
        self.user_tweets = {} # map of user and tweets
        
    def parse_hashtag(self, file_name):
        f = open(file_name,"r")
        for line in f:
            try:
                data = cjson.decode(line)
                if "entities" in data and "user" in data:
                    if "hashtags" in data["entities"]:
                        for tag in data["entities"]["hashtags"]:
                            ft = open("tag_tweets/%s.json" %(tag["text"].lower()),"a")
                            tag_tweets = {"screen_name":data["user"]["screen_name"], "id":data["user"]["id"], "text":data["text"]}
                            ft.write(cjson.encode(tag_tweets)+"\n")
                            ft.close()
                            if not tag["text"].lower() in self.hashtag_dic:
                                self.hashtag_dic.update({tag["text"].lower() : 1})
                            else:
                                self.hashtag_dic[tag["text"].lower()] = self.hashtag_dic[tag["text"].lower()] + 1
            except:
                print line
                pass
        f.close()
        
        for key in self.hashtag_dic:
            self.hashtag_list.append([key, self.hashtag_dic[key]])
        
        self.hashtag_list = sorted(self.hashtag_list, key=lambda tup:tup[1], reverse=True)
        
        fl = open("hashtag_list.txt","w")
        for e in self.hashtag_list:
            fl.write(e[0]+" "+str(e[1])+"\n")
        fl.close()
        
    def rank_hashtag(self):
        print "ranked hashtag"

class parse_usertweets:
    def __init__(self):
        self.user_tweets = {}
        self.features = ["text", "favorite_count", "retweet_count", "retweeted", "entities", "created_at", "user"]
        
    def parse_usertweets(self, file_name):
        f = open(file_name,"r")
        for line in f:
            try:
                data = cjson.decode(line)
                if "entities" in data and "user" in data:
                    pass
            
            except:
                print line
                pass
        f.close()

def main():
    myhashtag = hashtag()
    myhashtag.parse_hashtag("../twitter_crawler/user_data/user_tweets.json")

if __name__ == "__main__":
    main()
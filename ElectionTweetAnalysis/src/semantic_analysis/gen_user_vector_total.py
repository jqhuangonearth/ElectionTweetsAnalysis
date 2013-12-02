"""
This program generate the user_vector for all sampled user, whose file size is 738MB
The file is in "/home/bolun/git/ElectionTweetsAnalysis/ElectionTweetAnalysis/src/
twitter_crawler/user_data/user_tweets.json"
@author: Bolun Huang
"""
import cjson
import json

class gen_user_vector:
    def __init__(self):
        self.user_profiles = {}
        self.user_vectors = {}
        self.profile_features = ["id", "followers_count", "friends_count",
                                 "statuses_count", "description", "screen_name"]
        
        self.tweet_features = ["text", "created_at", "lang"]
        
    def get_user_vectors(self):
        f = open("/home/bolun/git/ElectionTweetsAnalysis/ElectionTweetAnalysis/src/twitter_crawler/user_data/user_tweets.json","r")
        for line in f:
            try:
                data = cjson.decode(line)
                if "user" in data:
                    if not data["user"]["screen_name"] in self.user_profiles:
                        self.user_profiles.update({ data["user"]["screen_name"] : {key : data["user"][key] for key in self.profile_features}})
                    tweet = { key : data[key] for key in self.tweet_features}
                    tweet.update({"tweet_id" : data["id"]})
                    tweet.update(self.get_entities(data))
                    if not data["user"]["screen_name"] in self.user_vectors:
                        self.user_vectors.update({ data["user"]["screen_name"] : {"tweets": [tweet]}})
                    else:
                        self.user_vectors[data["user"]["screen_name"]]["tweets"].append(tweet)
            except:
                #print line
                pass
        f.close()
        
        print len(self.user_profiles), len(self.user_vectors)

        delete_list = []
        for user in self.user_vectors:
            if user in self.user_profiles:
                self.user_vectors[user].update(self.user_profiles[user])
            else:
                delete_list.append(user)
        print len(delete_list)
        for user in delete_list:
            self.user_vectors.pop(user)
        print len(self.user_vectors)
        count = 0
        for user in self.user_vectors:
            self.user_vectors[user].update({"_id" : count})
            count += 1
        
        f = open("user_vector/user_vector_total.json","w")
        for user in self.user_vectors:
            json.dump(self.user_vectors[user], f)
            f.write("\n")
        f.close()
    
    
    def get_entities(self, jsonobj):
        """
        get the user mentions, hashtag and urls for the user
        """
        entities = {"user_mentions" : [], "hashtags": [], "urls": []} # default entity object
        if not jsonobj == None and type(jsonobj) is dict:
            if "entities" in jsonobj:
                if "user_mentions" in jsonobj["entities"] and len(jsonobj["entities"]["user_mentions"]) > 0:
                    user_mentions = {}
                    for user in jsonobj["entities"]["user_mentions"]:
                        try:
                            user_mentions = {key : user[key] for key in ["id","creen_name"]}
                            entities["user_mentions"].append(user_mentions)
                        except:
                            pass

                if "hashtags" in jsonobj and len(jsonobj["entities"]["hashtags"]) > 0:
                    tag_list = []
                    for tag in jsonobj["entities"]["hashtags"]:
                        try:
                            tag_list.append(tag["text"])
                        except:
                            pass
                    entities["hashtags"] = tag_list
                if "urls" in jsonobj and len(jsonobj["entities"]["urls"]) > 0:
                    url_list = []
                    for tag in jsonobj["entities"]["urls"]:
                        try:
                            url_list.append(tag["text"])
                        except:
                            pass
                    entities["urls"] = url_list
        else:
            print "cannot get_entities() for non-dict type: ", jsonobj
        return entities
    
def main():
    guv = gen_user_vector()
    guv.get_user_vectors()

if __name__ == "__main__":
    main()
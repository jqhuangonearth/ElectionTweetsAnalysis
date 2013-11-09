"""
@author: Bolun Huang
@description: process the user data into user tweets
one user per file containing all its tweets
process user profile into another folder
one user per file containing its corresponding profile
in self.target_user_dic, value = 1 is democrat, value = 0
is republican
"""
import cjson
import json

class data_preprocess:
    def __init__(self):
        self.infile = None
        self.ulistfile = None
        self.user_dic = {}
        self.target_user_dic = {}
        
    def process(self, filename):
        self.infile = open(filename, "r")
        i = 1
        for line in self.infile:
            data = {}
            user_profile = {}
            try:
                data = cjson.decode(line)
                if "user" in data:
                    if "screen_name" in data["user"]:
                        name = data["user"]["screen_name"]
                        print i, name
                        if name not in self.user_dic:
                            self.user_dic.update({name : 1}) # update user list
                            # write on user_tweet file
                            f_tweet = open("user_tweets/%s.json" %(name), "a")
                            user_profile = data.pop("user")
                            json.dump(data, f_tweet)
                            f_tweet.write("\n")
                            f_tweet.close()
                            
                            f_profile = open("user_profile/%s.json" %(name), "w")
                            json.dump(user_profile, f_profile)
                            f_profile.write("\n")
                            f_profile.close()
                            
                        else:
                            self.user_dic[name] += 1 # update user list
                            # write on user_profile file
                            f_tweet = open("user_tweets/%s.json" %(name), "a")
                            user_profile = data.pop("user")
                            json.dump(data, f_tweet)
                            f_tweet.write("\n")
                            f_tweet.close()
                        i += 1
            except Exception as e:
                print e, name
        self.infile.close()

    def generate_user_vector(self, filename):
        
        self.ulistfile = open(filename, "r")
        for line in self.ulistfile:
            if not line.startswith("#"):                    
                line = line.split()
                if not line[0] in self.target_user_dic:
                    if line[2] == "d":
                        self.target_user_dic.update({line[0] : 1}) # democract
                    elif line[2] == "r":
                        self.target_user_dic.update({line[0] : 0}) # republican
                    else:
                        pass
        self.ulistfile.close()
                
        f_vector = open("user_vector/user_vector.json", "w")
        
        profile_key = ["id", 
                       "screen_name", 
                       "name", 
                       "created_at", 
                       "description", 
                       "followers_count", 
                       "friends_count", 
                       "statuses_count", 
                       "favourites_count", 
                       "listed_count"]
        failed_user = []
        
        for user in self.target_user_dic:
            user_vector = {}
            tweets = []
            try:
                f_profile = open("user_profile/%s.json" %(user), "r")
                for line in f_profile:
                    data = cjson.decode(line)
                    user_vector = {key: data[key] for key in profile_key}
                f_profile.close()
                f_tweet = open("user_tweets/%s.json" %(user), "r")
                for line in f_tweet:
                    data = cjson.decode(line)
                    tweet = {"text" : data["text"], 
                             "user_mentions" : [[x["screen_name"], x["id"]] for x in data["entities"]["user_mentions"]], 
                             "hashtags" : data["entities"]["hashtags"],
                             "urls" : data["entities"]["urls"],
                             "retweet_count" : data["retweet_count"],
                             "geo" : data["geo"],
                             "created_at" : data["created_at"],
                             "place" : data["place"]}
                    tweets.append(tweet)
                user_vector["tweets"] = tweets
                user_vector["class"] = self.target_user_dic[user]
                f_tweet.close()
                json.dump(user_vector, f_vector)
                f_vector.write("\n")
            except Exception as e:
                print e, user
                failed_user.append(user)
                pass
        f_vector.close()
        
        f_labelled_user_new = open("data/labelled_user_new.txt", "w")
        self.ulistfile = open(filename, "r")
        for line in self.ulistfile:
            l = line.split()
            if l[0] in failed_user:
                pass
            else:
                f_labelled_user_new.write(line)
        self.ulistfile.close()
        
        f_labelled_user_new.close()


def main():
    m = data_preprocess()
    #m.process()
    m.generate_user_vector("data/labelled_user.txt")
    
    
if __name__ == "__main__":
    main()
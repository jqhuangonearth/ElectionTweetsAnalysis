"""
construct new user vector for 393 users from ../src/tweets file
"""

import cjson
from pymongo import Connection
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import time as time
from time import gmtime, strftime
from stats import histogram
import math

tweet_features = ["urls", "tx", "t", "h"]

class construct_vector:
    DB_SERVER = "localhost"
    DB_PORT = 27017
    DB_NAME = "electiontweetsanalysis"
    COLLECTION_UV = "user_profile"
    def __init__(self):
        self.user_vector = {}
        self.G = nx.DiGraph()
        f = open("data/labelled_user_new.txt","r")
        for line in f:
            if not line.startswith("#"):
                line = line.split(" ")
                label = 0
                if line[2] == "r":
                    label = 1
                self.user_vector.update({line[0].strip() : {"tweets": [], "class" : label}})
        f.close()
        
    def read_tweet_file(self):
        global tweet_features
        f = open("../tweets","r")
        for line in f:
            data = cjson.decode(line)
            if data["u"]["sn"] in self.user_vector:
                tweet = {key : data[key] for key in tweet_features}
                tweet.update({"id" : len(self.user_vector[data["u"]["sn"]])})
                self.user_vector[data["u"]["sn"]]["tweets"].append(tweet)
        f.close()
        
    def import_to_db(self):
        connection = Connection(self.DB_SERVER, self.DB_PORT)
        db = connection[self.DB_NAME]
        for user in self.user_vector:
            it = db[self.COLLECTION_UV].find({'screen_name': user})
            for i in it:
                i.update({"tweets" : self.user_vector[user]["tweets"]})
                i.update({"tweets_count" : len(self.user_vector[user]["tweets"])})
                print user, len(self.user_vector[user]["tweets"])
                db[self.COLLECTION_UV].update({'screen_name': user}, i)

    def get_normal_features(self):
        connection = Connection(self.DB_SERVER, self.DB_PORT)
        db = connection[self.DB_NAME]
        user_friends = self.read_user_friends("../twitter_crawler/social_graph/user_friends.json")
        user_followers = self.read_user_friends("../twitter_crawler/social_graph/user_followers.json")
        print user_friends.keys()
        for node in self.user_vector:
            it = db[self.COLLECTION_UV].find({'screen_name': node})
            for i in it:
                """label"""
                #i.update({"class" : self.user_vector[node]["class"]})
                """URL ratio + retweet ratio"""
                """total_count = len(i["tweets"])
                url_count = 0
                retweet_count = 0
                for tweet in i["tweets"]:
                    if len(tweet["urls"]) != 0:
                        url_count += 1
                    if tweet["tx"].startswith("RT"):
                        retweet_count += 1
                i.update({ "url_ratio" : url_count/float(total_count)})
                i.update({ "retweet_ratio" : retweet_count/float(total_count)})
                """
                """url_uniqueness"""
                """tweet similarity"""
                """X_train = []
                texts = []
                for tweet in i["tweets"]:
                    texts.append(tweet["tx"].lower())
                self.vectorizer = TfidfVectorizer(min_df=1, max_features=1000, stop_words='english')
                X_train = self.vectorizer.fit_transform(texts).toarray()
                similarity = 0.0
                if len(X_train) == 0:
                    similarity = 0.0
                elif len(X_train) == 1:
                    similarity = 1.0
                else:
                    h = histogram()
                    for k in range(len(X_train)-1):
                        for j in xrange(k+1, len(X_train)):
                            h.add(histogram.cosine_distance(X_train[k], X_train[j]))
                    similarity = h.avg()
                i.update({"tweet_similarity" : similarity})"""
                """time variance"""
                """t_list = []
                for tweet in i["tweets"]:
                    t = tweet['t'].split(' +0000')
                    ts = t[0]+t[1]
                    ti = time.mktime(time.strptime(strftime(ts)))
                    t_list.append(ti)
                h = histogram()
                for j in range(len(t_list)-1):
                    h.add(t_list[j+1]-t_list[j])
                #print h.std()
                i.update({"interval_variance" : h.std()})"""
                """unique_mention"""
                """mention_list = []
                for tweet in i["tweets"]:
                    for word in tweet["tx"].lower().split(" "):
                        if word.startswith("@"):
                            for w in word.strip(":").split("@"):
                                if w != "":
                                    mention_list.append(w)
                mention_list_wod = list(set(mention_list))
                i.update({"unique_mention" : (len(mention_list_wod)+1) / float(len(mention_list)+1)})"""
                """polarity"""
                """r_count = 0
                o_count = 0
                for tweet in i["tweets"]:
                    if (tweet["tx"].lower().__contains__("obama") or tweet["tx"].lower().__contains__("biden") or 
                        tweet["tx"].lower().__contains__("democrat")):
                        o_count += 1
                    if (tweet["tx"].lower().__contains__("romney") or tweet["tx"].lower().__contains__("mitt") or 
                        tweet["tx"].lower().__contains__("paul") or tweet["tx"].lower().__contains__("ryan") or
                        tweet["tx"].lower().__contains__("republican")):
                        r_count += 1
                i.update({"polarity" : (r_count-o_count) / float(len(i["tweets"]))})
                """
                """unique_url"""
                """url_list = []
                for tweet in i["tweets"]:
                    if tweet["urls"] != None:
                        for url in tweet["urls"]:
                            if url != None:
                                url_list.append(url.split("\\\/\\\/")[1].split("\\\/")[0])
                url_list_wod = list(set(url_list))
                unique_url = 0
                if len(url_list) != 0:
                    unique_url = len(url_list_wod) / float(len(url_list))
                i.update({"unique_url" : unique_url})"""
                """FlFratio"""
                """FlFratio = 0.0
                if user_friends.has_key(node) and user_followers.has_key(node):
                    intersect = set(user_friends[node]).intersection(set(user_followers[node]))
                    FlFratio = len(intersect) / float(len(user_friends[node]))
                i.update({"FlFratio" : FlFratio})
                """
                #db[self.COLLECTION_UV].update({'screen_name': node}, i)
    
    @staticmethod
    def read_user_friends(filename):
        user_friends = {}
        f = open(filename, "r")
        for line in f:
            data = cjson.decode(line)
            user_friends.update(data)
        f.close()
        return user_friends

    def build_graph(self):
        fg = open("../social_analysis/user_graph/user_graph_393_screen_name_2.txt", "r")
        flag = 0
        node_list = []
        edge_list = []
        for line in fg:
            if flag == 1 and not line.startswith("#"):
                try:
                    nodes = line.split(" ")
                    node_list.append(nodes[0].rstrip())
                except:
                    pass
            elif flag == 2 and not line.startswith("#"):
                try:
                    edge = line.split(" ")
                    edge_list.append([edge[0].rstrip(), edge[1].rstrip()])
                except:
                    pass
            if line.startswith("#nodes"):
                flag = 1
            elif line.startswith("#edges"):
                flag = 2
        fg.close()
        self.construct_graph(node_list, edge_list)
        
    def construct_graph(self, node_list, edge_list):
        """
        @type node_list: list
        @param node_list: list of uid of users
        
        @type edge_list: list of two tuple list
        @param edge_list: list of edges represented by [uid1, uid2]
        """
        for node in node_list:
            self.G.add_node(node)
        for edge in edge_list:
            self.G.add_edge(edge[0], edge[1])
    
def main():
    c = construct_vector()
    #c.read_tweet_file()
    #c.import_to_db()
    c.get_normal_features()
    
if __name__ == "__main__":
    main()
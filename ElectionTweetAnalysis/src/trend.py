import cjson
import os
import httplib2
import urllib
import random
from pymongo import Connection
import matplotlib.pyplot as plt
import networkx as nx

class trend():
    special_chars = ['~','!','@','#','$','%','^','&','*','(',')','_','+','`','-','=','[',']','\\','{','}','|',';',"'",':','"',',','.','/','<','>','?']
    DB_SERVER = "localhost" 
    DB_PORT = 27017
    DB_NAME = "election_analysis"
    COLLECTION_UV = "user_vector"
    def __init__(self, user_file, trend_count_file):
        #<user_name,tweets_count> key value pairs
        self.trends = {}
        self.dic_users = {}
        self.trends_list = []
        self.hashtag = {}
        self.user_ids = []
        self.G = nx.DiGraph() # tag_graph
        self.f = open(user_file, 'r')
        lines = self.f.readlines()
        for i in lines:
            data = i.strip().split()
            self.user_ids.append(data[0])
            #self.dic_users.update({data[0]:data[2]})
        self.f.close()
        self.fo = open(trend_count_file, 'w')
        self.connection = Connection(self.DB_SERVER, self.DB_PORT)
        self.db = self.connection[self.DB_NAME]
        
    def train_trend(self):
        for user in self.user_ids:
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                tweet = i['tweets']
                #print tweet
                for j in tweet:
                    tmp = j.lower()
                    tmp = tmp.split()
                    for k in tmp:
                        if k.startswith("#"):
                            k1 = k.strip("#")
                            if len(k1) != 0:
                                if not k1 in self.trends:
                                    self.trends.update({k1 : 1})
                                else:
                                    self.trends[k1] += 1
        print self.trends
        print len(self.trends)
        
    def sort(self):
        for trend in self.trends:
            self.trends_list.append([trend, int(self.trends[trend])])
        result = self.mergesort(self.trends_list)
        print result
        for trend in result:
            self.fo.write('%s %d\n' %(trend[0], trend[1]))
        self.fo.close()
    
    def mergesort(self,lst):
        if len(lst) <= 1:
            return lst
        middle = int( len(lst) / 2 )
        left = self.mergesort(lst[:middle])
        right = self.mergesort(lst[middle:])
        return merge(left, right)
    
    def hash_tag(self):
        l = [] ## trend list
        fh = open('data/trends_2.txt','r')
        for line in fh:
            line = line.split()
            l.append(line[0])
        fh.close()
        print l
        f = open('data/trends_user_2.txt','w')
        for user in self.user_ids:
            user_tag_dic = {}
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                tweet = i['tweets']
                for j in tweet:
                    tmp = j.lower()
                    tmp = tmp.split()
                    for k in tmp:
                        if k.startswith("#"):
                            k1 = k.strip("#")
                            if k1 in l:
                                if not k1 in user_tag_dic:
                                    user_tag_dic.update({k1 : 1})
                                else:
                                    user_tag_dic[k1] += 1
            print user, len(user_tag_dic), user_tag_dic
            f.write('%s ' %(user))
            for i in user_tag_dic:
                f.write('%s<>%d ' %(i, user_tag_dic[i]))
            f.write('\n')
        f.close()
        
    def get_tag_feature(self):
        f = open('data/trends_user_2.txt','r')
        user_tags = {}
        for line in f:
            line.strip()
            line = line.split()
            user_tags.update({line[0]:{}})
            if len(line) > 1:
                for i in line[1:]:
                    i.strip()
                    sep = i.split('<>')
                    user_tags[line[0]].update({sep[0]:int(sep[1])})
        f.close()
        print user_tags
        ### write to database
        for user in user_tags:
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                i.update({'tag_count' : len(user_tags[user])})
                self.db[self.COLLECTION_UV].update({'_id': user}, i)
        #exit(0)
        obama = ['obama', 'biden']
        romney = ['romney', 'mitt', 'ryan']
        for user in user_tags:
            tag_count_obama = 0
            tag_count_romney = 0
            for tag in user_tags[user]:
                if ('obama' in tag or 'biden' in tag) and ('romney' not in tag or 'mitt' not in tag or 'ryan' not in tag):
                    tag_count_obama += user_tags[user][tag]
                elif ('romney' in tag or 'mitt' in tag or 'ryan' in tag) and ('obama' not in tag or 'biden' not in tag):
                    tag_count_romney += user_tags[user][tag]
            sum = tag_count_obama + tag_count_romney
            if sum != 0:
                tag_polarity = abs(tag_count_obama - tag_count_romney)**2
            else:
                tag_polarity = 0
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                i.update({'tag_polarity': tag_polarity})
                self.db[self.COLLECTION_UV].update({'_id': user}, i)
            self.G.add_node(user, label = user)
        tag_users_list = []
        result = []
        for trend in self.trends_list:
            tag_users_list.append(trend[0])
        print tag_users_list
        for i in range(0, len(tag_users_list)):
            result.append([])
            for user in user_tags:
                if tag_users_list[i] in user_tags[user]:
                    result[i].append(user)
            print tag_users_list[i], result[i]
        print len(tag_users_list), len(result)
        for r in result:
            for i in range(0, len(r)-1):
                for j in range(0, len(r)):
                    self.G.add_edge(r[i], r[j], weight = 1)
        #self.G.add_edge(user, sn, weight = 1)
        '''
        labels=dict((n,d['label']) for n,d in self.G.nodes(data=True))
        val_map = {}
        for user in self.dic_users:
            if self.dic_users[user] == 'c':
                val_map.update({ user : 'r'})
            elif self.dic_users[user] == 's':
                val_map.update({ user : 'y'})
            elif self.dic_users[user] == 'j':
                val_map.update({ user : 'g'})
            else:
                val_map.update({ user : 'b'})
        values = [val_map.get(node) for node in self.G.nodes()]
        self.G = self.G.to_undirected()
        nx.draw(self.G, pos = nx.spring_layout(self.G, dim = 2), randomcmap = plt.get_cmap('jet'), node_color = values, width = 1, node_size = 40, with_labels=True)
        plt.show()
        '''
        
def merge(left, right):
    result = []
    i ,j = 0, 0
    while i < len(left) and j < len(right):
        if left[i][1] > right[j][1]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result += left[i:]
    result += right[j:]
    return result
    
        
def main():
    tr = trend('user_data/labelled_new_into_db.txt','data/trends_2.txt')
    tr.train_trend()
    tr.sort()
    tr.hash_tag()
    tr.get_tag_feature()
    
if __name__ == "__main__":
    main()
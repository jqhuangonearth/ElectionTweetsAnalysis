'''
@summary: clissfier
@author: Bolun Huang
'''

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn import metrics
from pymongo import Connection
import random

class UserClassifier:
    DB_SERVER = "localhost"
    DB_PORT = 27017
    DB_NAME = "election_analysis"
    COLLECTION_UV = "user_vector"
    def __init__(self, labelled_user_ids_file):
        f = open(labelled_user_ids_file, 'r')
        self.dic_ids = {}
        for line in f:
            line = line.split()
            if len(line) >= 3:
                self.dic_ids.update({ line[0] : {'class' : line[2]}})
            #else:
            #    self.dic_ids.update({ line[0] : {'class' : 'x'}})
        #print self.dic_ids['LOLGOP']['class']
        self.connection = Connection(self.DB_SERVER, self.DB_PORT)
        self.db = self.connection[self.DB_NAME]
        self.features = [#'mention_in_degree', 
                    #'mention_out_degree', 
                    'avg_interval', 
                    'var_interval', 
                    'tweet_similarity',
                    'sentiment_abortion',
                    'sentiment_obamacare',
                    'sentiment_guncontrol',
                    'sentiment_immigration',
                    'sentiment_edu',
                    'sentiment_military',
                    'sentiment_economic',
                    'sentiment_bengahzi',
                    'sentiment_chrysler',
                    'sentiment_fraud',
                    'sentiment_obama',
                    'sentiment_romney'
                    ]
        self.sentiments = ['sentiment_abortion',
                    'sentiment_obamacare',
                    'sentiment_guncontrol',
                    'sentiment_immigration',
                    'sentiment_edu',
                    'sentiment_military',
                    'sentiment_economic',
                    'sentiment_bengahzi',
                    'sentiment_chrysler',
                    'sentiment_fraud',
                    'sentiment_obama',
                    'sentiment_romney'
                    ]
        
    def label_class(self):
        for user in self.dic_ids:
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                if self.dic_ids[user]['class'] == 'c':
                    i.update({'new_class': 0})
                elif self.dic_ids[user]['class'] == 'n':
                    i.update({'new_class': 1})
                elif self.dic_ids[user]['class'] == 's':
                    i.update({'new_class': 0})
                elif self.dic_ids[user]['class'] == 'j':
                    i.update({'new_class': 2})
                self.db[self.COLLECTION_UV].update({'_id': user}, i)
    def add_new_features(self):
        '''
        f = open('data/mention.txt','r')
        f.readline()
        for i in f.readlines():
            i = i.split()
            #print self.dic_ids[i[0]]
            if i[0] in self.dic_ids:
                self.dic_ids[i[0]].update({'mention_in_degree': int(i[4])})
                self.dic_ids[i[0]].update({'mention_out_degree': int(i[3])})
        f.close()
        '''
        f = open('data/timeline_2.txt','r')
        f.readline()
        for i in f.readlines():
            i = i.split()
            if i[0] in self.dic_ids:
                #print self.dic_ids[i[0]]
                self.dic_ids[i[0]].update({'avg_interval': float(i[1])})
                self.dic_ids[i[0]].update({'var_interval': float(i[2])})
        f.close()
        f = open('data/tweet_variance_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                self.dic_ids[i[0]].update({'tweet_similarity': float(i[1])})
        f.close()
        #### abortion ####
        f = open('data/topic_abortion_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_abortion': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_abortion': float(i[2])})
        f.close()
        #### obamacare ####
        f = open('data/topic_obamacare_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_obamacare': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_obamacare': float(i[2])})
        f.close()
        #### guncontrol ####
        f = open('data/topic_gun_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_guncontrol': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_guncontrol': float(i[2])})
        f.close()
        #### immigration ####
        f = open('data/topic_immigration_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_immigration': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_immigration': float(i[2])})
        f.close()
        #### edu ####
        f = open('data/topic_edu_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_edu': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_edu': float(i[2])})
        f.close()
        #### military ####
        f = open('data/topic_military_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_military': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_military': float(i[2])})
        f.close()
        #### economic ####
        f = open('data/topic_economy_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_economic': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_economic': float(i[2])})
        f.close()
        #### bengahzi ####
        f = open('data/topic_bengahzi_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_bengahzi': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_bengahzi': float(i[2])})
        f.close()
        #### chrysler ####
        f = open('data/topic_chrysler_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_chrysler': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_chrysler': float(i[2])})
        f.close()
        #### fraud ####
        f = open('data/topic_fraud_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_fraud': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_fraud': float(i[2])})
        f.close()
        #### obama ####
        f = open('data/topic_obama_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_obama': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_obama': float(i[2])})
        f.close()
        #### romney ####
        f = open('data/topic_romney_sentimantic_2.txt','r')
        for i in f:
            i = i.split()
            if i[0] in self.dic_ids:
                if float(i[2]) < 0:
                    self.dic_ids[i[0]].update({'sentiment_romney': float(i[2])*(-1.0)})
                else:
                    self.dic_ids[i[0]].update({'sentiment_romney': float(i[2])})
        f.close()
        ### write into the databse ####
        print self.dic_ids
        for user in self.dic_ids:
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                for f in self.features:
                    i.update({f: self.dic_ids[user][f]})
                self.db[self.COLLECTION_UV].update({'_id': user}, i)
    
    def add_topic_sentiment(self):
        for user in self.dic_ids:
            topic_sentiment = 0.0
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                for f in self.sentiments:
                    if i[f] < 0:
                        topic_sentiment += -i[f]
                    else:
                        topic_sentiment += i[f]
                i.update({'topic_sentiment':topic_sentiment})
                #print user, topic_sentiment
                self.db[self.COLLECTION_UV].update({'_id': user}, i)
    
    def add_following_follower_ratio(self):
        for user in self.dic_ids:
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                i['following_follower_ratio'] = 0.0
                i.update({'following_follower_ratio': i['friends_count']/float(i['followers_count']+1)})
                self.db[self.COLLECTION_UV].update({'_id': user}, i)
    
    def add_url(self):
        f = open('data/url_2.txt','r')
        for i in f:
            i = i.split()
            #print self.dic_ids[i[0]]
            self.dic_ids[i[0]].update({'url_percentage': float(i[1])})
        f.close()
        for user in self.dic_ids:
            it = self.db[self.COLLECTION_UV].find({'_id': user})
            for i in it:
                i.update({'url_percentage': self.dic_ids[user]['url_percentage']})
                self.db[self.COLLECTION_UV].update({'_id': user}, i)

def sort():
    f = open('user_data/labelled_users_new_2.txt','r')
    i_c = []
    i_s = []
    i_n = []
    i_j = []
    for l in f:
        l = l.split()
        if len(l) == 3:
            l.append('pad')
        if l[2] == 'c':
            i_c.append([l[0],l[1],l[2],l[3]])
        elif l[2] == 's':
            i_s.append([l[0],l[1],l[2],l[3]])
        elif l[2] == 'n':
            i_n.append([l[0],l[1],l[2],l[3]])
        elif l[2] == 'j':
            i_j.append([l[0],l[1],l[2],l[3]])
    f.close()
    swap = 1
    while swap == 1:
        swap = 0
        for i in range(0,len(i_c)-1):
            if int(i_c[i][1]) < int(i_c[i+1][1]):
                temp = i_c[i+1]
                i_c[i+1] = i_c[i]
                i_c[i] = temp
                swap = 1
    swap = 1
    while swap == 1:
        swap = 0
        for i in range(0,len(i_s)-1):
            if int(i_s[i][1]) < int(i_s[i+1][1]):
                temp = i_s[i+1]
                i_s[i+1] = i_s[i]
                i_s[i] = temp
                swap = 1
    swap = 1
    while swap == 1:
        swap = 0
        for i in range(0,len(i_n)-1):
            if int(i_n[i][1]) < int(i_n[i+1][1]):
                temp = i_n[i+1]
                i_n[i+1] = i_n[i]
                i_n[i] = temp
                swap = 1
    swap = 1
    while swap == 1:
        swap = 0
        for i in range(0,len(i_j)-1):
            if int(i_j[i][1]) < int(i_j[i+1][1]):
                temp = i_j[i+1]
                i_j[i+1] = i_j[i]
                i_j[i] = temp
                swap = 1
    f = open('user_data/labelled_user_new_2_sorted.txt','w')
    for l in i_c:
        f.write('{} '.format(l[0]).ljust(20)+'{} '.format(l[1]).ljust(10)+'{} '.format(l[2]).ljust(10)+l[3]+'\n')
    for l in i_s:
        f.write('{} '.format(l[0]).ljust(20)+'{} '.format(l[1]).ljust(10)+'{} '.format(l[2]).ljust(10)+l[3]+'\n')
    for l in i_n:
        f.write('{} '.format(l[0]).ljust(20)+'{} '.format(l[1]).ljust(10)+'{} '.format(l[2]).ljust(10)+l[3]+'\n')
    for l in i_j:
        f.write('{} '.format(l[0]).ljust(20)+'{} '.format(l[1]).ljust(10)+'{} '.format(l[2]).ljust(10)+l[3]+'\n')
    f.close()
    
    
        
def main():
    uc = UserClassifier('user_data/labelled_new.txt')
    uc.label_class()
    #sort()
    #uc.add_new_features()
    #uc.add_topic_sentiment()
    #uc.add_following_follower_ratio()
    #uc.add_url()

    
if __name__ == "__main__":
    main()
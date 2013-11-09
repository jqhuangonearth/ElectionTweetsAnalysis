'''
@author: Bolun Huang
@summary: explore text feature in tweets
'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn import metrics
import random
from pymongo import Connection
import cjson
import matplotlib.pyplot as plt
import math

class text_features():
    def __init__(self):
        self.data_ids = []
        self.data_tweets = []
        self.data_types = []
        self.tweet_variance = []
        self.f = open("user_data/labelled_new_into_db.txt", "r")
        sum = 0
        for line in self.f.readlines():
            line = line.split()
            self.data_ids.append(line[0])
            self.data_tweets.append(line[1])
            self.data_types.append('1')
            sum = sum + int(line[1])
        print len(self.data_ids)
        print sum
        
    def text_features(self):
        #user_vectors_train = []
        for i in range(0, len(self.data_ids)):
            ii = self.data_ids[i]
            texts = []
            f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(ii), "r")
            for line in f:
                data = cjson.decode(line)
                if 'tx' in data:
                    texts.append(data['tx'])
                if ':x' in data:
                    texts.append(data[':x'])
            f.close()
            self.vectorizer = TfidfVectorizer(min_df=1, max_features=1000, stop_words='english')
            X_train = self.vectorizer.fit_transform(texts)
            X_tr = X_train.toarray()
            #print len(X_tr)
            #print X_tr
            #print 'num text features: ', len(self.vectorizer.get_feature_names())
            variance_vec = self.calculate_variance(X_tr)
            self.tweet_variance.append(variance_vec)
        
    def calculate_variance(self, vect):
        sum1 = 0.0
        #count = 0
        for i in range(0, len(vect)-1):
            for j in range(i, len(vect)):
                dot = 0.0
                sum_vector1 = 0.0
                sum_vector2 = 0.0
                for index in range(0, len(vect[i])):
                    dot = vect[i][index]*vect[j][index] + dot
                    sum_vector1 = sum_vector1 + vect[i][index]*vect[i][index]
                    sum_vector2 = sum_vector2 + vect[j][index]*vect[j][index]
                norm_vector1 = math.sqrt(sum_vector1)
                norm_vector2 = math.sqrt(sum_vector2)
                cosine_sim = dot/float(norm_vector1*norm_vector2)
                sum1 = cosine_sim + sum1
        #print cosine_sim
                #count = count + 1
        return sum1/float(len(vect)*(len(vect)-1)*0.5)
    
    def analysis(self):
        print self.tweet_variance
        dic = {}
        #print len(self.data_ids)
        #print len(self.data_tweets)
        #print len(self.data_types)
        for i in range(0, len(self.data_ids)):
            dic.update({self.data_ids[i] : [self.data_types[i], self.tweet_variance[i]]})
        f = open('data/tweet_variance_2.txt','w')
        for user in dic:
            f.write('{} '.format(user).ljust(20)+'%s\n' %(dic[user][1]))
        f.close()
    
    '''      
    def draw(self):
        y = 1
        camp_var_sum = 0.0
        camp_var_num = 0
        nor_var_sum = 0.0
        nor_var_num = 0
        dic = {}
        #print len(self.data_ids)
        #print len(self.data_tweets)
        #print len(self.data_types)
        
        #for i in range(0, len(self.data_ids)):
        #    dic.update({self.data_ids[i] : [self.data_types[i]]})
        
        dic_2 = {}
        f = open('data/text_tweet_variance_2.txt','r')
        for line in f:
            line = line.split()
            dic_2.update({line[0] : float(line[1])})
        f.close()
        for user in dic:
            dic[user].append(dic_2[user])
        print dic
        
        for user in dic:
            if dic[user][0] == 'c':
                #for t in self.dic[user][5]:
                plt.plot(dic[user][1], y, 'ro')
                camp_var_sum = camp_var_sum + dic[user][1]
                camp_var_num = camp_var_num + 1
            elif dic[user][0] == 's':
                #for t in self.dic[user][5]:
                plt.plot(dic[user][1], y, 'yo')
                camp_var_sum = camp_var_sum + dic[user][1]
                camp_var_num = camp_var_num + 1
            elif dic[user][0] == 'n':
                plt.plot(dic[user][1], y, 'bo')
                nor_var_sum = nor_var_sum + dic[user][1]
                nor_var_num = nor_var_num + 1
            else:
                plt.plot(dic[user][1], y, 'go')
                nor_var_sum = nor_var_sum + dic[user][1]
                nor_var_num = nor_var_num + 1
            y = y + 1
        camp_avg = camp_var_sum/float(camp_var_num)
        nor_avg = nor_var_sum/float(nor_var_num)
        print 'average tweet similarity'
        print 'campaigner:  ', camp_avg
        print 'normal user: ', nor_avg
        
        plt.show()
    '''
        
def main():
    tf = text_features()
    tf.text_features()
    tf.analysis()
    #tf.draw()
if __name__ == "__main__":
    main()
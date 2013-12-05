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

class text_features():
    def __init__(self):
        self.data_ids = []
        self.data_tweets = []
        self.data_types = []
        self.tweet_variance = []
        self.f = open("user_data/labelled_users_new.txt", "r")
        sum = 0
        for line in self.f.readlines():
            line = line.split()
            self.data_ids.append(line[0])
            self.data_tweets.append(line[1])
            self.data_types.append(line[2])
            sum = sum + int(line[1])
        print len(self.data_ids)
        print sum
        
    def text_features(self):
        user_vectors_train = []
        texts = []
        for i in self.data_ids:
            f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(i), "r")
            for line in f:
                data = cjson.decode(line)
                if 'tx' in data:
                    texts.append(' '.join(data['tx']))
                if ':x' in data:
                    texts.append(' '.join(data[':x']))
                
            f.close()
        self.vectorizer = TfidfVectorizer(min_df=1, max_features=1000, stop_words='english')
        X_train = self.vectorizer.fit_transform(texts)
        X_tr = X_train.toarray()
        print len(X_tr)
        #print 'num text features: ', len(self.vectorizer.get_feature_names())
        
        print self.data_tweets
        index = 0
        for i in self.data_tweets:
            user_tweets_vector = []
            count = 0
            #print i
            ii = int(i)
            while (count < ii):
                #print count
                #print i
                ind = index+count
                #print ind
                user_tweets_vector.append(X_tr[ind])
                #print count
                count = count + 1
            index = index + ii
            print index
            variance_vec = self.calculate_variance(user_tweets_vector)
            self.tweet_variance.append(variance_vec)
            
        '''
        self.central_vector = []
        val = 0
        for i in range(0, len(X_tr[0])):
            for j in range(0, len(X_tr)):
                val = val + X_tr[j][i]
            #print j #1 less, so plus 1
            self.central_vector.append(val/float(j+1))
        #print self.central_vector
        '''
        #print len(X_tr)
        #print X_tr[0]
        #for i in range(0, len(X_tr[0])):
        #    print X_tr[0][i], 
        #print X_tr
        
    def calculate_variance(self, vect):
        sum = 0
        count = 0
        for i in range(0, len(vect)-1):
            for j in range(i, len(vect)):
                dot_mul = 0
                for index in range(0, len(vect[i])):
                    dot_mul = vect[i][index]*vect[j][index] + dot_mul
                sum = dot_mul + sum
                count = count + 1
        return sum/count
    
    def analysis(self):
        print self.tweet_variance
        dic = {}
        print len(self.data_ids)
        print len(self.data_tweets)
        print len(self.data_types)
        for i in range(0, len(self.data_ids)):
            dic.update({self.data_ids[i] : [self.data_types[i], self.tweet_variance[i]]})
        y = 1
        for user in dic:
            if dic[user][0] == 'c':
                #for t in self.dic[user][5]:
                plt.plot(dic[user][1], y, 'ro')
            else:
                #for t in self.dic[user][5]:
                plt.plot(dic[user][1], y, 'bo')
            y = y + 1
        plt.show()
        
def main():
    tf = text_features()
    tf.text_features()
    tf.analysis()
    
if __name__ == "__main__":
    main()
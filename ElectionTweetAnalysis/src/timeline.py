'''
@author: Bolun Huang
@summary: To calculate the time stamps of the users and the time metrics, such as avg_tweet_interval, 
variance_of_tweet_interval, percentage of tweets in debate, distance of tweet from debate time
'''
import random
import cjson
import time as time
from time import gmtime, strftime
import matplotlib.pyplot as plt
import networkx as nx
import math

class time_line():
    def __init__(self):
        f = open("user_data/labelled_new_into_db.txt","r")
        self.dic = {}
        #f.readline()
        for line in f.readlines():
            line = line.split()
            if len(line) == 4:
                self.dic.update({ line[0] : [line[1], line[2]] })
            else:
                self.dic.update({ line[0] : [line[1], 'x'] })
        #f1 = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/", "r")
        print len(self.dic)
        f.close()
        
    def time_stamp(self):
        for user in self.dic:
            #c = 0
            print user
            f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(user), "r")
            '''store tweet time stamps'''
            self.dic[user].append([])
            '''store debate related tweet time stamps'''
            self.dic[user].append([])
            for line in f: # go over all the tweets of the user
                data = cjson.decode(line)
                #print data['t']
                t = data['t'].split(' +0000')
                ts = t[0]+t[1]
                ti = time.mktime(time.strptime(strftime(ts)))
                self.dic[user][2].append(ti)
                #tweet = data['tx']
                #if 'debate' in tweet:
                #    self.dic[user][3].append(ti)
                    #c = c + 1
                #print ti
            #print c
            print self.dic[user][2]
            # the dictionary becomes: { user : [num_tweets, type, [list of time stamp]]}
            f.close()
    '''Analyzing time related metrics: avg_interval; '''
    def time_analysis(self):
        '''avg_interval'''
        # sort all the list
        for user in self.dic:
            swap = 1
            while swap == 1:
                swap = 0
                for i in range(0, len(self.dic[user][2])-1):
                    if self.dic[user][2][i] > self.dic[user][2][i+1]:
                        tmp = self.dic[user][2][i+1]
                        self.dic[user][2][i+1] = self.dic[user][2][i]
                        self.dic[user][2][i] = tmp
                        swap = 1
            #print self.dic[user][6]
        for user in self.dic:
            count = 0
            sum = 0
            '''to store all tweet intervals'''
            self.dic[user].append([])
            for i in range(0, len(self.dic[user][2])-1):
                interval = self.dic[user][2][i+1] - self.dic[user][2][i]
                self.dic[user][4].append(interval)
                sum = interval + sum
                count = count + 1
            avg_interval = sum/float(count)
            '''add 'average_tweet_interval' to the dictionary (8th value of user)'''
            self.dic[user].append(avg_interval)
            print self.dic[user][4]
        '''variance_of_tweet_intervals'''
        for user in self.dic:
            variance = 0
            for i in self.dic[user][4]:
                variance = math.pow((i-self.dic[user][5]), 2)+variance
            '''user[9] = variance of tweet interval'''
            self.dic[user].append(math.sqrt(variance))
            #print math.sqrt(variance)
            
    def plot_time_line(self):
        y = 1
        for user in self.dic:
            if self.dic[user][1] == 'c' or self.dic[user][1] == 's':
                #for t in self.dic[user][5]:
                plt.plot(self.dic[user][6], y, 'ro')
            elif self.dic[user][1] == 'n' or self.dic[user][1] == 'j':
                #for t in self.dic[user][5]:
                plt.plot(self.dic[user][6], y, 'bo')
            else:
                plt.plot(self.dic[user][6], y, 'go')
            y = y + 1
        plt.show()
    def save_file(self):
        f = open("data/timeline_2.txt", "w")
        f.write('{} '.format("user").ljust(20)+'{} '.format("avg_interval").ljust(15)+'{} '.format("var_interval").ljust(15)+'\n')
        for user in self.dic:
            f.write('{} '.format(user).ljust(20)+'{} '.format(str(self.dic[user][5])).ljust(15)+'{} '.format(str(self.dic[user][6])).ljust(15)+'\n')
        f.close()
    
def main():
    tl = time_line()
    tl.time_stamp()
    tl.time_analysis()
    tl.plot_time_line()
    tl.save_file()
    
if __name__ == "__main__":
    main()
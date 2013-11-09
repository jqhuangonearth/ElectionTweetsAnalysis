'''
@URL: http://2012election.procon.org/view.source-summary-chart.php
'''

import cjson
import subprocess
import re
import nltk
from nltk.corpus import stopwords

class topic():
    def __init__(self):
        self.lda = '/home/bolun/hbl/GibbsLDA++-0.2/src/lda'
        self.f = open('labelled_users_new.txt', 'r')
        self.f1 = open('data/topics_tweets.txt', 'w')
        #f2 = open(outfile+'.full', 'w')
        
    def get_tweettexts(self):
        user = []
        for l in self.f:
            l = l.split()
            user.append(l[0])
        for u in user:
            f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(u), "r")
            for line in f: # each tweet
                data = cjson.decode(line)
                if 'tx' in data:
                    tx = self.get_processed_tweet(data['tx'])
                if ':x' in data:
                    tx = self.get_processed_tweet(data[':x'])
                if tx != '':
                    self.f1.write(tx+'\n')
                    #f2.write(cjson.encode(data)+'\n')
            self.f.close()
        self.f1.close()
        #f2.close()

    """
    strip the non-english and other useless characters from the tweets
    """
    def get_processed_tweet(self, tweet, stopwords=True):
        text = tweet.lower()
        text = re.sub(r'(@\w+\s?)|(@\s+)', '', text)
        text = re.sub(r'\b%s\b' %('obama'), '', text)
        text = re.sub(r'\b%s\b' %('election'), '', text)
        text = re.sub(r'\b%s\b' %('rt'), '', text)
        text = re.sub(r'\b%s\b' %('romney'), '', text)
        text = re.sub(r'\b%s\b' %('republican'), '', text)
        text = re.sub(r'\b%s\b' %('democrat'), '', text)
        text = re.sub(r'\b%s\b' %('paul ryan'), '', text)
        text = re.sub(r'\b%s\b' %('biden'), '', text)
        text = re.sub(r'\b%s\b' %('mitt'), '', text)
        text = re.sub(r'\b%s\b' %('vote'), '', text)
        text = re.sub(r'\b%s\b' %('president'), '', text)
        text = re.sub(r'\b%s\b' %('elections'), '', text)
        text = re.sub(r'http:[\\/.a-z0-9]+\s?', '', text)
        text = text.encode('ascii', 'ignore')
        text = re.sub(r'[;:\)\(\?\'\"!,.@#-+*/\\]', ' ', text)
        text = ' '.join(text.split())
        #print text
        if stopwords:
            text = self.filter_stopwords(text)
        return text.strip()

    def filter_stopwords(self, tweet):
        words = nltk.word_tokenize(tweet)
        final = []
        for w in words:
            if w in stopwords.words('english'):
                continue
            final.append(w)
        return ' '.join(final)

    def find_category_clusters_lda(self):
        k=10
        twords=50
        self.f1 = open('data/topics_tweets.txt', 'r')
        lines = self.f1.readlines()
        self.f1.close()
        f2 = open('/home/bolun/workspace/ElectionTweetsAnalysis/src/topics/topics_tweets.txt', 'w')
        f2.write(str(len(lines)) + '\n')
        f2.writelines(lines)
        f2.close()
        infile = '/home/bolun/workspace/ElectionTweetsAnalysis/src/topics/topics_tweets.txt'
        subprocess.call([self.lda, '-est', '-ntopics', str(k), '-twords', str(twords), '-savestep', str(3000), '-dfile', infile, '-niters', str(6000)])
        '''
        f = open('model-final.theta', 'r')
        f1 = open(objfile, 'r')
        for l in f:
            probs = l.split()
            obj = f1.readline()
            probs = [float(x) for x in probs]
            topic = -1
            maxprob = -1
            for i in range(len(probs)):
                if probs[i] > maxprob:
                    maxprob = probs[i]
                    topic = i
            f2 = open(cluster_outfolder + 'cluster' + str(topic), 'a')
            f2.write(obj)
            f2.close()
        f1.close()
        f.close()'''

def main():
    t = topic()
    t.get_tweettexts()
    t.find_category_clusters_lda()
    
    
if __name__ == "__main__":
    main()

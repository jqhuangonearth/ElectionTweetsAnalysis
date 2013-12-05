'''
@author: BOlun Huang
@summary: URL percent
'''
import cjson

def url():
    f = open('user_data/labelled_new_into_db.txt','r')
    f_out = open('data/url_2.txt','w')
    dic = {}
    for l in f:
        l = l.split()
        dic.update({l[0]: 0.0})
    f.close()
    for user in dic:
        tweet_count = 0
        url_count = 0
        f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(user), "r")
        for line in f:
            data = cjson.decode(line)
            tweet_count += 1
            if not len(data['urls']) == 0:
                url_count += 1
        f.close()
        dic[user] = url_count/float(tweet_count)
        f_out.write('{} '.format(user).ljust(20)+"%.4f\n" %(dic[user]))
    print dic
    f_out.close()
    
def main():
    url()
    
if __name__ == "__main__":
    main()
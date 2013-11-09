"""
@description: this program feed tweets containing particular topic to alchamy api
then returns a distribution of semantic score of that topic
"""

import cjson
import httplib2
import urllib
import re
import stats
import sys

class topic_semantic_check:
    def __init__(self):
        self.APIKEY = urllib.quote_plus('c8231ecbb8f6dbe91199d3318a6a604ac24e5da9')
        self.http = httplib2.Http()
        self.hashtag_list = get_hashtag_list("hashtag_list.txt")
        self.output = open("output/tag_statistics.csv", "w")
        self.record = open("output/record.txt","w")
        
    def check(self, tag):
        mystats = stats.histogram()
        score_list = []
        target_user_list = self.get_targeting_users("/home/bolun/workspace/ElectionTweetsAnalysis/src/user_data/labelled_new.txt")
        count_labelled_all = 0 # number of tweets of the labelled
        count_neutral = 0 # number of neutral tweets of the labelled
        count_aligned = 0 # number of aligned tweets of the labelled
        covered_user = []
        ft = open("tag_tweets/%s.json" %(tag),"r")
        for line in ft:
            content = cjson.decode(line)
            if content["screen_name"] in target_user_list:
                if not content["screen_name"] in covered_user:
                    covered_user.append(content["screen_name"])
                text = content["text"].lower()
                text = re.sub(r'http:[\\/.a-z0-9]+\s?', '', text)
                #text = re.sub(r'(@\w+\s?)|(@\s+)', '', text)
                #text = re.sub(r'[@#-+*]', ' ', text)
                #text = re.sub(r'rt\s?', '', text)
                text = text.strip()
                query = 'http://access.alchemyapi.com/calls/text/TextGetTextSentiment?apikey={0}&text={1}&outputMode=json'.format(self.APIKEY, urllib.quote_plus(text.encode('utf8')))
                (header, context) = self.http.request(query, 'GET')
                if header and header['status'] == '200':
                    result = cjson.decode(context)
                    if result['status'] == 'OK':
                        count_labelled_all += 1
                        if result['docSentiment']['type'] == 'neutral':
                            count_neutral += 1
                        elif float(result['docSentiment']['score']) > 0.01 or float(result['docSentiment']['score']) < -0.01:
                            score_list.append(float(result['docSentiment']['score']))
                            mystats.add(float(result['docSentiment']['score']))
                            count_aligned += 1
                        else:
                            count_neutral += 1
                    else:
                        print "error: ", result
                else:
                    print "error tag: ", tag
                    pass
        ft.close()
        if count_labelled_all == 0:
            aligned_per = 0.0
        else:
            aligned_per = count_aligned/float(count_labelled_all)
        coverage = len(covered_user)/float(len(target_user_list))
        print "done tag:", tag
        #[index, distribution] = mystats.histogram_fixed("/home/bolun/workspace/ElectionTweetsAnalysis/src/semantic_analysis/output/%s.png" %tag)
        self.output.write(tag+","+str(count_labelled_all)+","+str(count_neutral)+","+str(count_aligned)+","+str(aligned_per)
                          +","+str(coverage)+","+str(mystats.count_neg())+","+str(mystats.avg_neg())+","+str(mystats.count_pos())+","+str(mystats.avg_pos())
                          +","+str(mystats.std())+","+str(mystats.min())+","+str(mystats.max())+"\n")
        #self.record.write("tag: %s\n" %tag)
        #self.record.write("index: "+str(index)+"\n")
        #self.record.write("distr: "+str(distribution)+"\n")
        #self.record.write("\n")
        
    def get_targeting_users(self, filename):
        user_list = []
        f = open(filename, "r")
        for line in f:
            line = line.split()
            if line[2] == "c" or line[2] == "s": # only extract those non-neutral users
                user_list.append(line[0])
        f.close()
        return user_list
    
    def run(self):
        self.output.write("tag,count,count_neutral,count_aligned,aligned/total,coverage,count_neg,avg_neg,count_pos,avg_pos,std,min,max\n")
        i = 0
        for tag in self.hashtag_list:
            # tag = self.hashtag_list[9][0]
            # self.check(tag[0])
            i += 1
            if i > 743:
                self.check(tag[0])
                #break
        self.output.close()
        self.record.close()
     
def get_hashtag_list(filename):
    f = open(filename, "r")
    mylist = []
    sum1 = 0
    for line in f:
        line = line.split()
        sum1 += int(line[1])
        mylist.append([line[0], int(line[1])])
    return mylist

def main():
    mycheck = topic_semantic_check()
    mycheck.run()
    
if __name__ == "__main__":
    main()
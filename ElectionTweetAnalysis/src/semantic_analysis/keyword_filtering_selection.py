"""
@author: Bolun Huang
This program consider those keywords:
1) with > 200 frequencies in the total recent new dataset
2) rank them by generating the sentiment distribution with 
only that words excluding the other candidate words
3) find the diff between pos sentiment score and neg sentiment
score for the particular keywords
"""
from pymongo import Connection
import cjson
import json
import static_func
import math
import stats
from pylab import rcParams
import matplotlib.pyplot as plt

OUT_DIR = "/home/bolun/ElectionTweetAnalysis_results/sentiword_rank/"
SUB_DIR_1 = "hashtag_sentiment_figures/"
SUB_DIR_2 = "hashtag_sentiword_figures/"
SUB_DIR_3 = "hashtag_sentiscore_figures/"

class sentiment_keyword_selection:
    DB_HOST = "localhost"
    DB_PORT = 27017
    DB_NAME = "electiontweetsanalysis"
    COLLECTION_UV = "user_vector_campainers"
    def __init__(self):
        self.keywords = {}
        #self.hashtags = {}
        self.en_word_dict = set()
        self.connection = Connection(self.DB_HOST, self.DB_PORT)
        self.db = self.connection[self.DB_NAME]
        self.scores = ["sentiword_score","sentiment_score"]
    
    def get_en_dict_word(self):
        f = open("/usr/share/dict/american-english","r")
        for line in f:
            self.en_word_dict.add(line.rstrip())
        f.close()
        
    def contains_spchar(self, text):
        """
        @type text: string
        @param text: a string
        @return: false if the string doesn't contains special char (except lowercase letters); otherwise true
        """
        for c in text:
            if not ord(c) >= 97 and ord(c) <= 122:
                return True
        return False
        
    def get_hashtags(self):
        it = self.db[self.COLLECTION_UV].find()
        for i in it:
            for tweet in i["tweets"]:
                if len(tweet["hashtags"]) > 0:
                    for tag in tweet["hashtags"]:
                        tg = tag["text"].lower()
                        if tg not in self.keywords:
                            self.keywords.update({tg : {"user_count" : 0, "count" : 0, "tag_count" : 1, "scores" : []}})
                            self.keywords[tg]["scores"].append(self.get_scores(tweet))
                        else:
                            self.keywords[tg]["tag_count"] = self.keywords[tg]["tag_count"] + 1
                            self.keywords[tg]["scores"].append(self.get_scores(tweet))
        it = self.db[self.COLLECTION_UV].find()
        for i in it:
            user_word_dic = {}
            for tweet in i["tweets"]:
                words = static_func.static_fucntions.process_sentence(tweet["text"])
                words_dict = {}
                for word in words:
                    if not words_dict.has_key(word):
                        words_dict.update({word : 1})
                    else:
                        words_dict[word] += 1
                    if not user_word_dic.has_key(word):
                        user_word_dic.update({word : 1})
                    else:
                        user_word_dic[word] += 1
                for word in words_dict:
                    if self.keywords.has_key(word):
                        self.keywords[word]["count"] += words_dict[word]
            for word in user_word_dic:
                if self.keywords.has_key(word):
                    self.keywords[word]["user_count"] += 1
    
    def save_htag_file(self):
        f = open("topics/hashtag_counts_senti_scores.json","w")
        json.dump(self.keywords, f)
        f.close()   
        
        hashtag_list = sorted(self.keywords.iteritems(), key = lambda x : x[1]["count"], reverse = True)
        f = open("topics/hashtag_distributions.csv","w")
        f.write("tag,usercount,count,tagcount\n")
        for tag in hashtag_list:
            f.write(tag[0]+","+str(tag[1]["user_count"])+","+str(tag[1]["count"])+","+str(tag[1]["tag_count"])+"\n")
        f.close()
        
    def get_scores(self, jsontweet):
        scores = {}
        for item in self.scores:
            if jsontweet[item] == None:
                scores.update({item : 0.0})
            else:
                scores.update({item : jsontweet[item]})
        sentiscore = 0.0 # MAX/MIN of sentiment_score and sentiword_score
        if scores["sentiment_score"] >= 0 and scores["sentiword_score"] >= 0:
            sentiscore = max(scores["sentiment_score"], scores["sentiword_score"])
        elif scores["sentiment_score"] < 0 and scores["sentiword_score"] < 0:
            sentiscore = min(scores["sentiment_score"], scores["sentiword_score"])
        else:
            try:
                if math.fabs(scores["sentiment_score"]) > math.fabs(scores["sentiword_score"]):
                    sentiscore = scores["sentiment_score"]
                else:
                    sentiscore = scores["sentiword_score"]
            except:
                print scores
        scores.update({"sentiscore" : sentiscore})
        return scores
        
    def get_keywords(self, rm_en =True):
        if rm_en:
            self.get_en_dict_word()
        
        #self.get_term_distributions()
        self.read_reduced_tags()
        
        print len(self.keywords)
        #exit(0)
        it = self.db[self.COLLECTION_UV].find()
        for i in it:
            for tweet in i["tweets"]:
                if len(tweet["hashtags"]) > 0:
                    for tag in tweet["hashtags"]:
                        tg = tag["text"].lower()
                        if tg in self.keywords:
                            #self.keywords.update({tg : {"user_count" : 0, "count" : 0, "tag_count" : 1, "scores" : []}})
                            self.keywords[tg]["scores"].append(self.get_scores(tweet))
                        else:
                            #self.keywords[tg]["tag_count"] = self.keywords[tg]["tag_count"] + 1
                            #self.keywords[tg]["scores"].append(self.get_scores(tweet))
                            pass
        
        """
        it = self.db[self.COLLECTION_UV].find()
        for i in it:
            for tweet in i["tweets"]:
                words = static_func.static_fucntions.process_sentence(tweet["text"])
                word_dict = {}
                for word in words:
                    if self.keywords.has_key(word):
                        if not word_dict.has_key(word):
                            word_dict.update({word : 1})
                        else:
                            word_dict[word] += 1
                    else:
                        pass
                scores = {}
                for item in self.scores:
                    if tweet[item] == None:
                        scores.update({item : 0.0})
                    else:
                        scores.update({item : tweet[item]})
                sentiscore = 0.0 # MAX/MIN of sentiment_score and sentiword_score
                if scores["sentiment_score"] >= 0 and scores["sentiword_score"] >= 0:
                    sentiscore = max(scores["sentiment_score"], scores["sentiword_score"])
                elif scores["sentiment_score"] < 0 and scores["sentiword_score"] < 0:
                    sentiscore = min(scores["sentiment_score"], scores["sentiword_score"])
                else:
                    try:
                        if math.fabs(scores["sentiment_score"]) > math.fabs(scores["sentiword_score"]):
                            sentiscore = scores["sentiment_score"]
                        else:
                            sentiscore = scores["sentiword_score"]
                    except:
                        print scores
                scores.update({"sentiscore" : sentiscore})
                if len(word_dict) == 1:
                    for word in word_dict:
                        self.keywords[word]["scores"].append(scores)"""
        #print self.keywords
    
    def read_keywords(self, rm_en = True):
        if rm_en:
            self.get_en_dict_word()
        f = open("topics/hashtag_senti_scores.json","r")
        self.keywords = cjson.decode(f.readline())
        f.close()
        delete_list = []
        if rm_en:
            for word in self.keywords:
                if word in self.en_word_dict:
                    delete_list.append(word)
            for word in delete_list:
                self.keywords.pop(word)
        
    def read_reduced_tags(self):
        f = open("topics/hashtag_distributions_reduced.csv","r")
        line = f.readline()
        
        for line in f:
            line = line.split(";")
            self.keywords.update({line[0] : {"user_count" : int(line[1]), "count" : int(line[2]), "tag_count" : int(line[3]), "scores" : []}})
        f.close()
    
    def get_term_distributions(self):
        f = open("topics/term_distributions.txt", "r")
        for line in f:
            line = line.split()
            if int(line[1]) > 500 and not self.contains_spchar(line[0]):
                self.keywords.update({line[0] : {"count" : int(line[1]), "scores" : []}})
        f.close()
    
    def save_file(self):
        f = open("topics/term_senti_scores_%d.json" %len(self.keywords),"w")
        json.dump(self.keywords, f)
        f.close()

    def keyword_distribution(self, rm_en = True):
        
        f = open("results/statistics_hashtag_sentiscores_%d.csv" %len(self.keywords),"w")
        f.write("keyword,user_count,tag_count,count,sw_avg_neg,sw_avg_pos,sw_count_neg,sw_count_zero,sw_count_pos,sw_min,sw_max,"
                       +"st_avg_neg,st_avg_pos,st_count_neg,st_count_zero,st_count_pos,st_min,st_max,"
                       +"sc_avg_neg,sc_avg_pos,sc_count_neg,sc_count_zero,sc_count_pos,sc_min,sc_max\n")
        for word in self.keywords:
            hsw = stats.histogram()
            hst = stats.histogram()
            has = stats.histogram()
            for score in self.keywords[word]["scores"]:
                hsw.add(score["sentiword_score"])
                hst.add(score["sentiment_score"])
                has.add(score["sentiscore"])
            
            f.write("%s,%d,%d,%d,%.3f,%.3f,%d,%d,%d,%.3f,%.3f," %(word, self.keywords[word]["user_count"], self.keywords[word]["tag_count"], hsw._count, 
                                                            hsw._mean_neg, hsw._mean_pos, hsw._count_neg, hsw._zero, hsw._count_pos, hsw._min, hsw._max))
            f.write("%.3f,%.3f,%d,%d,%d,%.3f,%.3f," %(hst._mean_neg, hst._mean_pos, hst._count_neg, hst._zero, hst._count_pos, hst._min, hst._max))
            f.write("%.3f,%.3f,%d,%d,%d,%.3f,%.3f\n" %(has._mean_neg, has._mean_pos, has._count_neg, has._zero, has._count_pos, has._min, has._max))
            
            distribution_sw = hsw.histogram_2()
            distribution_st = hst.histogram_2()
            distribution_as = has.histogram_2()
            
            # sentiword score
            x_axis = range(len(distribution_sw))
            rcParams['figure.figsize'] = 24, 5
            x_ = [-1.025 + i*0.05 for i in range(42)]
            plt.bar(x_axis, distribution_sw, width=0.8, facecolor='blue', alpha = 0.5)
            X_ticks = ["%.1f" %(x_[i]) for i in range(len(x_))]
            for i in range(len(X_ticks)):
                if (i-1)%2 != 0:
                    X_ticks[i] = ""
            plt.xticks(x_axis, X_ticks)
            plt.xlim(0, len(x_axis))
            plt.grid(True)
            plt.xlabel("Sentiword Score")
            plt.ylabel("Percentage (%)")
            plt.title("Sentiword Score Distribution - %s" %word)
            plt.savefig(OUT_DIR+SUB_DIR_1+"%s.png" %word,dpi=50)
            plt.clf()
            # sentiment score
            x_axis = range(len(distribution_st))
            rcParams['figure.figsize'] = 24, 5
            x_ = [-1.025 + i*0.05 for i in range(42)]
            plt.bar(x_axis, distribution_st, width=0.8, facecolor='blue', alpha = 0.5)
            X_ticks = ["%.1f" %(x_[i]) for i in range(len(x_))]
            for i in range(len(X_ticks)):
                if (i-1)%2 != 0:
                    X_ticks[i] = ""
            plt.xticks(x_axis, X_ticks)
            plt.xlim(0, len(x_axis))
            plt.grid(True)
            plt.xlabel("Sentiment Score")
            plt.ylabel("Percentage (%)")
            plt.title("Sentiment Score Distribution - %s" %word)
            plt.savefig(OUT_DIR+SUB_DIR_2+"%s.png" %word,dpi=50)
            plt.clf()                    
            # sentiscore score
            x_axis = range(len(distribution_as))
            rcParams['figure.figsize'] = 24, 5
            x_ = [-1.025 + i*0.05 for i in range(42)]
            plt.bar(x_axis, distribution_as, width=0.8, facecolor='blue', alpha = 0.5)
            X_ticks = ["%.1f" %(x_[i]) for i in range(len(x_))]
            for i in range(len(X_ticks)):
                if (i-1)%2 != 0:
                    X_ticks[i] = ""
            plt.xticks(x_axis, X_ticks)
            plt.xlim(0, len(x_axis))
            plt.grid(True)
            plt.xlabel("Avg Senti Score")
            plt.ylabel("Percentage (%)")
            plt.title("Senti Score Distribution - %s" %word)
            plt.savefig(OUT_DIR+SUB_DIR_3+"%s.png" %word, dpi=50)
            plt.clf()
            print "done %s: neutral_st %d neutral_sw %d neutral_as %d" %(word, hst.count_zero(), hsw.count_zero(), has.count_zero())
        f.close()
        
    def rank_keywords(self):
        print "rank_keywords"
        
    def statistics(self):
        print "statistics"
        
    
        
def main():
    sks = sentiment_keyword_selection()
    #sks.read_keywords(rm_en = False)
    #sks.save_file()
    #sks.get_hashtags()
    #sks.save_htag_file()
    #sks.read_reduced_tags()
    sks.get_keywords(rm_en = False)
    sks.keyword_distribution(rm_en = False)
    
if __name__ == "__main__":
    main()
        
    
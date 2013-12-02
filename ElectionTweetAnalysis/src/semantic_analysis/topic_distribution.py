"""
This program generates the sentiment distributions of topics
@author: Bolun Huang
"""
from pymongo import Connection
import re
import nltk
import cjson
import math
from pylab import rcParams
import matplotlib.pyplot as plt
import stats
import json

DB_SERVER = "localhost"
DB_PORT = 27017
DB_NAME = "electiontweetsanalysis"
COLLECTION_UV = "user_vector_campainers"

sentiword_folder = "results/sentiword_figures_2/"
pnword_folder = "results/pnword_figures_2/"
sentiment_folder = "results/sentiment_figures_2/"
sentiscore_folder = "results/sentiscore_figures_2/"

class topic_dist:
    def __init__(self):
        self.connection = Connection(DB_SERVER, DB_PORT)
        self.db = self.connection[DB_NAME]
        self.terms = {} # {term : {"sentiword_score": x, "pnword_score": x, "sentiment_socre": x}}
        self.user_dic = {}
        self.scores = ["sentiword_score",
                       "pnword_score",
                       "sentiment_score"]
        
    def get_term_dic(self):
        f = open("data/labelled_user_dic_393.json","r")
        self.user_dic = cjson.decode(f.readline())
        f.close()
        
        for user in self.user_dic:
            it = self.db[COLLECTION_UV].find({"screen_name" : user})
            for i in it:
                for tweet in i["tweets"]:
                    words = self.process_sentence(tweet["text"])
                    for word in words:
                        scores = [tweet[key] for key in self.scores]
                        sums = 0.0
                        count = 0
                        val = 0.0
                        for i in range(len(scores)):
                            if scores[i] != None and (scores[i] > 0.00 or scores[i] < -0.00) and i != 1: # dont count pnword score
                                sums += scores[i]
                                count += 1
                            else:
                                pass
                        if count != 0:
                            val = sums/float(count)
                        
                        if not self.terms.has_key(word):
                            self.terms.update({word : {"sentiword_score": [tweet["sentiword_score"]],
                                                      "pnword_score": [tweet["pnword_score"]],
                                                      "sentiment_score": [tweet["sentiment_score"]],
                                                      "avg_sentiscore" : [val]}})
                        else:
                            self.terms[word]["sentiword_score"].append(tweet["sentiword_score"])
                            self.terms[word]["pnword_score"].append(tweet["pnword_score"])
                            self.terms[word]["sentiment_score"].append(tweet["sentiment_score"])
                            self.terms[word]["avg_sentiscore"].append(val)
        
        print len(self.terms)
        
        f = open("topics/term_senti_scores.json","w")
        json.dump(self.terms, f)
        f.close()
        
                        
    def draw_distributions(self):
        """
        draw distributions for all terms in self.terms and save figs to specified folders
        """
        f = open("topics/term_senti_scores.json","r")
        self.terms = cjson.decode(f.readline())
        f.close()
        print len(self.terms)
        count = 0
        for term in self.terms:
                hsw = stats.histogram()
                #hpn = stats.histogram()
                hst = stats.histogram()
                has = stats.histogram()
                for s in self.terms[term]["sentiword_score"]:
                    hsw.add(s)
                #for s in self.terms[term]["pnword_score"]:
                #    hpn.add(s)
                for s in self.terms[term]["sentiment_score"]:
                    hst.add(s)
                for s in self.terms[term]["avg_sentiscore"]:
                    has.add(s)
                    
                distribution_sw = hsw.histogram_2()
                #distribution_pn = hpn.histogram_2()
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
                plt.title("Sentiword Score Distribution - %s" %term)
                plt.savefig(sentiword_folder+"%s.png" %term,dpi=50)
                plt.clf()
                """
                # positive negative score
                x_axis = range(len(distribution_pn))
                rcParams['figure.figsize'] = 24, 5
                x_ = [-1.025 + i*0.05 for i in range(42)]
                plt.bar(x_axis, distribution_pn, width=0.8, facecolor='blue', alpha = 0.5)
                X_ticks = ["%.1f" %(x_[i]) for i in range(len(x_))]
                for i in range(len(X_ticks)):
                    if (i-1)%2 != 0:
                        X_ticks[i] = ""
                plt.xticks(x_axis, X_ticks)
                plt.xlim(0, len(x_axis))
                plt.grid(True)
                plt.xlabel("Positive-Negative Word Score")
                plt.ylabel("Percentage (%)")
                plt.title("PNWord Score Distribution - %s" %term)
                plt.savefig(pnword_folder+"%s.png" %term,dpi=50)
                plt.clf()
                """
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
                plt.title("Sentiment Score Distribution - %s" %term)
                plt.savefig(sentiment_folder+"%s.png" %term,dpi=50)
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
                plt.title("Senti Score Distribution - %s" %term)
                plt.savefig(sentiscore_folder+"%s.png" %term, dpi=50)
                plt.clf()
                count += 1
                print "done %s: neutral_st %d neutral_sw %d neutral_as %d count %d" %(term, hst.count_zero(), hsw.count_zero(), has.count_zero(), count)
                
    def process_sentence(self, text):
        """
        process the sentence and return a list of lower case words/terms
        remove stopwords; remove url, '\'w'.
        """
        text1 = ""
        try:
            # to lower case
            text1 = text.lower()
            # remove url
            text1 = re.sub(r'http:[\\/.a-z0-9]+\s?', '', text1)
            text1 = re.sub(r'https:[\\/.a-z0-9]+\s?', '', text1)
            # rmove mentioned user names
            text1 = re.sub(r'(@\w+\s?)|(@\s+)', '', text1) 
            # remove special characters
            #text1 = re.sub(r'[\#\-\+\*\`\.\;\:\"\?\<\>\[\]\{\}\|\~\_\=\!\^\(\)]', '', text1) 
            # remove retweet tag
            text1 = re.sub(r'rt\s?', '', text1)
        except:
            print text1
            pass
        try:
            text1 = nltk.word_tokenize(text1)
        except:
            text1 = []
            pass
        words = []
        for i in range(len(text1)):
            tx = text1[i].encode('utf8')
            if self.has_special_chars(tx) or tx in nltk.corpus.stopwords.words('english'):
                pass
            else:
                words.append(text1[i].encode('utf8'))
        return words
    
    def has_special_chars(self, char):
        flag = 0
        for i in char:
            if (ord(i) >= 97 and ord(i) <= 122) or (ord(i) >= 48 and ord(i) <= 57):
                pass
            else:
                flag = 1 # invalid char detected!
                break
        if flag == 1:
            return True
        return False
        
def main():
    td = topic_dist()
    #td.get_term_dic()
    td.draw_distributions()
    
if __name__ == "__main__":
    main()
    
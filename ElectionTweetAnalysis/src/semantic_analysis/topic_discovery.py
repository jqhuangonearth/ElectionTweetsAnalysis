"""
This program discover topics from a corpus of documents
@author: Bolun Huang
"""
import cjson
import re
import nltk
import json
from stats import histogram
from pymongo import Connection
import math
import time

N = 200000

class topic_discovery:
    def __init__(self):
        self.tweets = []
        self.terms = {}
        self.sentiwords = {}
        self.user_vector = {}
        self.pos_words = []
        self.neg_words = []

    def get_tweets(self,filename):
        f = open(filename, "r")
        for line in f:
            data = cjson.decode(line)
            for tweet in data["tweets"]:
                self.tweets.append(tweet["text"])
        f.close()

    def gen_distribution(self):
        self.get_tweets("user_vector/user_vector.json")
        print len(self.tweets)
        #d_count = len(self.tweets) # total number of documents(tweets)
        for tweet in self.tweets:
            words = self.process_sentence(tweet)
            for word in words:
                if not self.terms.has_key(word):
                    self.terms.update({word : 1})
                else:
                    self.terms[word] += 1
                    
        l = sorted(self.terms.iteritems(), key = lambda x : x[1], reverse = True)
        f = open("topics/term_distributions.txt", "w")
        for item in l:
            f.write(item[0] + " " +str(item[1]) + "\n")
        f.close()

    def gen_tfidf(self):
        """
        TFIDF should be calculated not only in these users but all users we have
        including those neutral users so that we can pinpoint those stopwords
        """
        DB_SERVER = "localhost"
        DB_PORT = 27017
        DB_NAME = "electiontweetsanalysis"
        COLLECTION_UV = "user_vector_total"
        
        connection = Connection(DB_SERVER, DB_PORT)
        db = connection[DB_NAME]
        
        user_dic = {}
        
        f = open("data/user_1042.txt","r")
        for line in f:
            line = line.split(" ")
            user_dic.update({line[0].rstrip() : int(line[1].rstrip())})
        f.close()
        
        #print user_dic
        
        self.terms = {}
        count = 0
        for user in user_dic:
            it = db[COLLECTION_UV].find({"screen_name" : user})
            for i in it:
                for tweet in i["tweets"]:
                    count += 1
                    words = self.process_sentence(tweet["text"])
                    dist = {}
                    for word in words:
                        if not dist.has_key(word):
                            dist.update({word : 1})
                        else:
                            dist[word] += 1
                    for word in dist:
                        dist[word] = dist[word]/float(len(words))
                    for word in words:
                        if not self.terms.has_key(word):
                            self.terms.update({word : {"count" : 1, "tf_score" : {}}})
                        else:
                            self.terms[word]["count"] += 1
                    for word in dist:
                        self.terms[word]["tf_score"].update({tweet["tweet_id"] : dist[word]})
        
        print len(self.terms)
        
        for term in self.terms:
            self.terms[term].update({"idf" : count/float(len(self.terms[term]["tf_score"])+1)})
        
        f = open("topics/term_tfidf.json","w")
        json.dump(self.terms, f)
        f.close()
            
    def gen_pos_neg_word_dic(self):
        f = open("SentiWordNet/data/negative-words.txt","r")
        for line in f:
            if not line.startswith(";") and not line == "\n":
                self.neg_words.append(line.rstrip())
        f.close()
        
        f = open("SentiWordNet/data/positive-words.txt","r")
        for line in f:
            if not line.startswith(";"):
                self.pos_words.append(line.rstrip())
        f.close()
        
        f = open("SentiWordNet/data/negative_words_list.txt","w")
        for word in self.neg_words:
            f.write(word+"\n")
        f.close()
        
        f = open("SentiWordNet/data/positive_words_list.txt","w")
        for word in self.pos_words:
            f.write(word+"\n")
        f.close()
        
    def get_word_list(self, filename):
        word_dic = {}
        f = open(filename, "r")
        for line in f:
            word_dic.update({line.rstrip() : 1})
        f.close()
        return word_dic
        
        
    def get_sentiword_score(self):
        f = open("SentiWordNet/data/SentiWord.json","r")
        self.sentiwords = cjson.decode(f.readline())
        f.close()
        
        self.read_user_vector("user_vector/user_vector_new.json")
        self.neg_words = self.get_word_list("SentiWordNet/data/negative_words_list.txt")
        self.pos_words = self.get_word_list("SentiWordNet/data/positive_words_list.txt")
        
        myht = histogram()
        
        for user in self.user_vector:
            for tweet in self.user_vector[user]["tweets"]:
                words = self.process_sentence(tweet["text"])
                pnword_score = 0.0
                sentiword_score = 0.0
                sentiword_count = 0
                for word in words:
                    if self.sentiwords.has_key(word):
                        sentiword_score += self.sentiwords[word]
                        sentiword_count += 1
                    if self.pos_words.has_key(word):
                        pnword_score += 1.0
                    elif self.neg_words.has_key(word):
                        pnword_score -= 1.0
                myht.add(pnword_score)
                tweet.update({"pnword_score" : pnword_score})
                if sentiword_count != 0:
                    sentiword_score = sentiword_score/float(sentiword_count)
                tweet.update({"sentiword_score" : sentiword_score})
            
            #print self.user_vector[user]["tweets"]
        
        mean = myht.avg()
        std = myht.std()
        # normalize the positive_negative_word score
        for user in self.user_vector:
            for tweet in self.user_vector[user]["tweets"]:
                tweet["pnword_score"] = (tweet["pnword_score"]-mean)/std
                #print tweet["pnword_score"]
        
        f = open("user_vector/user_vector_new_2.json", "w")
        for user in self.user_vector:
            json.dump(self.user_vector[user], f)
            f.write("\n")
        f.close()
    
    def read_user_vector(self, filename):
        f = open(filename, "r")
        count = 0
        for line in f:
            data = cjson.decode(line)
            self.user_vector.update({ data["screen_name"] : data})
            count += 1
        f.close()

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
    
    def correlation_vector(self):
        """
        First filter out those with small coverage (number of tweets > 100);
        Then filter out those with small tfidf
        Find the correlation vectors and term graph according to the result of tfidf_dist
        """
        f = open("topics/term_tfidf.json","r")
        self.terms = cjson.decode(f.readline())
        f.close()
        
        #term_list = sorted(self.terms.iteritems(), key = lambda x : x[1]["count"], reverse = True)
        term_dic_truncated = {}
        
        for term in self.terms:
            if self.terms[term]["count"] > 100:
                term_dic_truncated.update({term : []})
                for tweet_id in self.terms[term]["tf_score"]:
                    term_dic_truncated[term].append(tweet_id)
        
        print len(term_dic_truncated)
        
        f = open("topic_graph/term_graph_2778.txt","a")
        f.write("#terms\n")
        for term in term_dic_truncated:
            f.write(term+"\n")
        f.write("#edges\n")
        f.close()
        
        term_list_truncated = list(term_dic_truncated.iteritems())
        cv_list = []
        for i in range(len(term_list_truncated)):
            N_k = len(term_list_truncated[i][1])
            print "start %s ..." %term_list_truncated[i][0]
            start = time.clock()
            for j in range(i+1, len(term_list_truncated)):
                N_z = len(term_list_truncated[j][1])
                R_kz = 0
                R_kz = self.find_size_of_common_sublist(term_list_truncated[i][1], term_list_truncated[j][1])
                if R_kz == 0:
                    cv_list.append([term_list_truncated[i][0], term_list_truncated[j][0], float("-inf")])
                    cv_list.append([term_list_truncated[j][0], term_list_truncated[i][0], float("-inf")])
                else:
                    try:
                        N_kz_1 = math.log((R_kz)/float(N_k - R_kz)/float(N_z - R_kz)*(N - N_z - N_k + R_kz))
                        N_kz_2 = math.fabs(R_kz/float(N_k)-(N_z - R_kz)/float(N - N_k))
                        N_zk_1 = math.log((R_kz)/float(N_z - R_kz)/float(N_k - R_kz)*(N - N_z - N_k + R_kz))
                        N_zk_2 = math.fabs(R_kz/float(N_z)-(N_k - R_kz)/float(N - N_z))
                        C_kz = N_kz_1*N_kz_2
                        C_zk = N_zk_1*N_zk_2
                        cv_list.append([term_list_truncated[i][0], term_list_truncated[j][0], C_kz])
                        cv_list.append([term_list_truncated[j][0], term_list_truncated[i][0], C_zk])
                    except:
                        cv_list.append([term_list_truncated[i][0], term_list_truncated[j][0], float("-inf")])
                        cv_list.append([term_list_truncated[j][0], term_list_truncated[i][0], float("-inf")])
                        pass
            # for every term and other terms, dump to file
            end = time.clock()
            print "done %s ... %.2fs" %(term_list_truncated[i][0], (end - start)) 
            f = open("topic_graph/term_graph_2778.txt","a")
            for cv in cv_list:
                f.write(cv[0]+" "+cv[1]+" "+str(cv[2])+"\n")
            f.close()
            cv_list = []
            
    
    def find_size_of_common_sublist(self, list1, list2):
        """
        @return: how many common elements in two lists; list has no duplicates
        """
        comm = 0
        dist = {}
        for item in list1:
            if not dist.has_key(item):
                dist.update({item : 1})
            else:
                dist[item] += 1
        for item in list2:
            if not dist.has_key(item):
                dist.update({item : 1})
            else:
                dist[item] += 1
        
        for item in dist:
            if dist[item] == 2:
                comm += 1
        return comm
    
def main():
    td = topic_discovery()
    #td.gen_distribution()
    #td.gen_tfidf()
    #td.get_sentiword_score()
    #td.gen_tfidf()
    #td.tfidf_dist()
    #td.correlation_vector()
    
if __name__ == "__main__":
    main()
"""
@author: Bolun Huang
"""

import cjson   
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn import metrics
from pymongo import Connection
import random

class Semantic_Based_Classifier:
    DB_SERVER = "localhost"
    DB_PORT = 27017
    DB_NAME = "electiontweetsanalysis"
    COLLECTION_UV = "user_vector_campainers"
    def __init__(self, alpha = 0.8):
        self.alpha = alpha
        f = open("results/adjusted_sentiscore_vector_%.1f.json" %self.alpha, "r")
        self.vector = cjson.decode(f.readline())
        f.close()

        self.data_ids = self.vector.keys()
        random.shuffle(self.data_ids)

        self.train_ids = []
        self.test_ids = []
        
        self.features = ["tcot", "syria", "p2", "bengahazi", "obama",
                         "teaparty", "uniteblue", "gop", "obamacare",
                         "tlot", "pjnet", "lnyhbt", "tgdn", "israel",
                         "ccot", "romney", "nra", "nsa", "irs"]
        self.connection = Connection(self.DB_SERVER, self.DB_PORT)
        self.db = self.connection[self.DB_NAME]
    
    def get_X_y(self, test_only=False):
        if not test_only:
            #training data
            X_tr, y_tr = [], []
            for user in self.train_ids:
                v = []
                for t in self.features:
                    v.append(self.vector[user][t])
                X_tr.append(v)
                
            for user in self.train_ids:
                it = self.db[self.COLLECTION_UV].find({"screen_name" : user})
                for i in it:
                    y_tr.append(i['class'])
            #print len(X_tr), len(y_tr)

        #test data
        X_te, y_te = [], []
        for user in self.test_ids:
            v = []
            for t in self.features:
                v.append(self.vector[user][t])
            X_te.append(v)
        
        for user in self.test_ids:
            it = self.db[self.COLLECTION_UV].find({"screen_name" : user})
            for i in it:
                y_te.append(i['class'])
        
        #print len(X_te), len(y_te)

        if test_only:
            return {'train': {'X': self.train_data['X'], 'y': self.train_data['y']}, 'test': {'X': X_te, 'y': y_te}}
        else:
            return {'train': {'X': X_tr, 'y': y_tr}, 'test': {'X': X_te, 'y': y_te}}

    def initialize_data(self, test_only=False):
        X_y_dict = self.get_X_y(test_only)
        if not test_only:
            self.train_data = X_y_dict['train']
        self.test_data = X_y_dict['test']

    def train(self):
        ### decision tree model
        self.clf = tree.DecisionTreeClassifier()
        self.clf = self.clf.fit(self.train_data['X'], self.train_data['y'])
        out = tree.export_graphviz(self.clf, out_file='data/decision_tree_adjusted_%.1f.dot' %self.alpha, feature_names=self.features)
        out.close()
        ### naive bayes model
        self.clf_2 = GaussianNB()
        self.clf_2.fit(self.train_data['X'], self.train_data['y'])
    
    def prediction(self):
        print "*******decision tree model********"
        y_predicted = self.clf.predict(self.test_data['X'])
        #y_predicted_prob = self.clf.predict_proba(self.test_data['X'])
        #print len(y_predicted), len(self.test_data['y'])
        score = metrics.f1_score(self.test_data['y'], y_predicted)
        print "f1-score:   %0.3f" % score
        #for i in range(0, len(self.test_data['y'])):
        #    print self.test_data['y'][i],
        #for i in range(0, len(y_predicted)):
        #    print y_predicted[i],
        print "classification report:"
        print metrics.classification_report(self.test_data['y'], y_predicted, target_names=['democrat','republican'])
        #print metrics.classification_report(self.test_data['y'], y_predicted, target_names=['other', 'journalist',''])

    def get_text_features(self):
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
            self.vectorizer = CountVectorizer()
            X_train = self.vectorizer.fit_transform(texts)
            X_tr = X_train.toarray()
            #print len(X_tr)
            #print X_tr
            #print 'num text features: ', len(self.vectorizer.get_feature_names())
            variance_vec = self.calculate_variance(X_tr)
            self.tweet_variance.append(variance_vec)

    def cross_validate(self, fold = 10):
        """
        Implement cross validation given the number of folds
        It first shuffle the ids and partition the id according
        to the given fold number
        @param fold: number of fold
        """
        random.shuffle(self.data_ids)
        data_size = len(self.data_ids)
        trunk_size = data_size/fold;
        for test in range(fold):
            self.train_ids = []
            self.test_ids = []
            # plitting the data
            for j in range(fold):
                if j == test and j != fold - 1:
                    self.test_ids.extend(self.data_ids[j*trunk_size:(j+1)*trunk_size])
                elif j == test and j == fold - 1:
                    self.test_ids.extend(self.data_ids[j*trunk_size:len(self.data_ids)])
                elif j != test and j != fold - 1:
                    self.train_ids.extend(self.data_ids[j*trunk_size:(j+1)*trunk_size])
                elif j != test and j == fold - 1:
                    self.train_ids.extend(self.data_ids[j*trunk_size:len(self.data_ids)])
            
            print "train:", len(self.train_ids), " test:", len(self.test_ids)
            #print self.test_ids
            self.initialize_data()
            self.train()
            self.prediction();    

    def test(self,ids_to_test):
        self.test_ids = ids_to_test
        self.initialize_data(True)
        y_predicted = self.clf.predict(self.test_data['X'])
        return y_predicted


def main():
    alphas = [0.1, 0.5, 0.8, 1.0]
    folds = [4, 5, 10]
    for a in alphas:
        uc = Semantic_Based_Classifier(alpha = a)
        print "*****************************************************"
        print "CROSS VALIDATION RESULT for alpha value = %.1f" %a
        #uc.initialize_data()
        #uc.train()
        #uc.prediction()
        for f in folds:
            print "%d FOLD CROSS VALIDATION.........................." %f
            uc.cross_validate(fold = f)
            print ""
        print "\t\t"

if __name__ == "__main__":
    main()

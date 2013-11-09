'''
semantic_based_classifier.py
@author: Vandana Bachani, Bolun Huang
@add based on semantic features grasped previously; I only care about democrats and republicans, no neutral guys
@in the database, class = 1, democrate; class = 0, republican
'''
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
	DB_NAME = "user_vector"
	COLLECTION_UV = "user_vector"
	def __init__(self, labelled_user_ids_file, train_percent):
		f = open(labelled_user_ids_file, 'r')
		self.data_ids = []
		self.ID_te = []
		for line in f:
			if not line.startswith("#"):
				line = line.split()
				self.data_ids.append(line[0])

		print self.data_ids
		print len(self.data_ids)
		random.shuffle(self.data_ids)

		num_ids = len(self.data_ids) * 1
		num_train = (train_percent/100.0) * num_ids
		self.train_ids = [self.data_ids[i].strip() for i in range(int(num_train))]
		print len(self.train_ids)
		#print self.train_ids
		self.test_ids = [self.data_ids[int(num_train+i)].strip() for i in range(int(num_ids - num_train))]
		print self.test_ids
		
		self.features = ["tcot",
						 "syria",
						 "p2",
						 "bengahazi",
						 "obama",
						 "teaparty",
						 "uniteblue",
						 "gop",
						 "obamacare",
						 "tlot",
						 "pjnet",
						 "lnyhbt",
						 "tgdn",
						 "israel",
						 "ccot",
						 "romneyryan2012",
						 "nra",
						 "nsa",
						 "irs"]
		
		self.connection = Connection(self.DB_SERVER, self.DB_PORT)
		self.db = self.connection[self.DB_NAME]
	
	def get_X_y(self, test_only=False):
		if not test_only:
			#training data
			user_vectors_train = []
			for i in self.train_ids:
				it = self.db[self.COLLECTION_UV].find({'_id': i})
				for j in it:
					user_vectors_train.append(j)

			X_tr, y_tr = [], []
			for i in user_vectors_train:
				X_tr.append(self.get_non_text_features(i))
				y_tr.append(i['class'])
				# print X_tr, y_tr

		#test data
		user_vectors_test = []
		for i in self.test_ids:
			it = self.db[self.COLLECTION_UV].find({'_id': i})
			for j in it:
				user_vectors_test.append(j)
				
		X_te, y_te = [], []
		for i in user_vectors_test:
			X_te.append(self.get_non_text_features(i))
			if(not test_only):
				y_te.append(i['class'])
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
		out = tree.export_graphviz(self.clf, out_file='data/decision_tree.dot')
		out.close()
		### naive bayes model
		self.clf_2 = GaussianNB()
		self.clf_2.fit(self.train_data['X'], self.train_data['y'])
	
	def prediction(self):
		print "**************decision tree model*****************"
		y_predicted = self.clf.predict(self.test_data['X'])
		#y_predicted_prob = self.clf.predict_proba(self.test_data['X'])
		print len(y_predicted), len(self.test_data['y'])
		score = metrics.f1_score(self.test_data['y'], y_predicted)
		print "f1-score:   %0.3f" % score
		print self.ID_te
		for i in range(0, len(self.test_data['y'])):
			print self.test_data['y'][i],
		print '\t'
		for i in range(0, len(y_predicted)):
			print y_predicted[i],
		print '\t'
		print "classification report:"
		print metrics.classification_report(self.test_data['y'], y_predicted, target_names=['campaigners','neutral'])
		#print metrics.classification_report(self.test_data['y'], y_predicted, target_names=['other', 'journalist',''])

	def get_non_text_features(self, user_vector):
		fs = [user_vector["tcot"],
			  user_vector["syria"],
			  user_vector["p2"],
			  user_vector["bengahazi"],
			  user_vector["obama"],
			  user_vector["teaparty"],
			  user_vector["uniteblue"],
			  user_vector["gop"],
			  user_vector["obamacare"],
			  user_vector["tlot"],
			  user_vector["pjnet"],
			  user_vector["lnyhbt"],
			  user_vector["tgdn"],
			  user_vector["israel"],
			  user_vector["ccot"],
			  user_vector["romneyryan2012"],
			  user_vector["nra"],
			  user_vector["nsa"],
			  user_vector["irs"]]

		return fs

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

	def cross_validate(self):
		data_size = len(self.data_ids)
		train_size = data_size/5;
		for j in range(5):
			start_idx = j*train_size
			end_idx = start_idx+train_size if start_idx+train_size < data_size else data_size
			#print "Train Data Start:",start_idx,"End",end_idx
			self.train_ids = [self.data_ids[i].strip() for i in range(start_idx,end_idx)]
			#print self.train_ids
			self.test_ids = [self.data_ids[i].strip() for i in range(0,start_idx)]
			if end_idx < data_size:
				self.test_ids.extend([self.data_ids[i].strip() for i in range(end_idx,data_size)])
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
	uc = Semantic_Based_Classifier('data/labelled_user_new.txt', 75)
	#uc.initialize_data()
	#uc.train()
	#uc.prediction()
	uc.cross_validate()

if __name__ == "__main__":
	main()

'''
classifier.py
@author: Bolun Huang
Classification of campaigners, supporters and neutral users from Election Tweets
'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn import metrics
from pymongo import Connection
import random
import cjson

class UserClassifier:
	DB_SERVER = "localhost"
	DB_PORT = 27017
	DB_NAME = "user_vector"
	COLLECTION_UV = "user_vector"
	def __init__(self, labelled_user_ids_file, train_percent):
		f = open(labelled_user_ids_file, 'r')
		self.data_ids = []
		for line in f:
			if not line.startswith("#"):
				line = line.split()
				#if int(line[1]) > 10:
				self.data_ids.append(line[0])
		f.close()
		print self.data_ids
		print "data_ids", len(self.data_ids)
		#random.shuffle(self.data_ids)

		num_ids = len(self.data_ids) * 1
		num_train = (train_percent/100.0) * num_ids
		self.train_ids = [self.data_ids[i] for i in range(int(num_train))]
		print "train_ids", len(self.train_ids), self.train_ids.__len__()
		print self.train_ids
		
		self.test_ids = [self.data_ids[int(num_train+i)].strip() for i in range(int(num_ids - num_train))]
		print "test_ids", len(self.test_ids), self.test_ids.__len__()
		print self.test_ids
		
		self.dataset = {}
		f = open("user_vector/user_vector_new.json", "r")
		for line in f:
			data = cjson.decode(line)
			if data["screen_name"] not in self.dataset:
				self.dataset.update({data["screen_name"] : data})
		f.close()
		
		print "dataset:", len(self.dataset)
		
		self.features = ['tcot',
						 'syria',
						 'p2',
						 'bengahazi',
						 'obama',
						 'teaparty',
						 'uniteblue',
						 'gop',
						 'obamacare',
						 'tlot',
						 'pjnet',
						 'lnyhbt',
						 'tgdn',
						 'israel',
						 'ccot',
						 'romneyryan2012',
						 'nra',
						 'nsa',
						 'irs']
	
	def get_X_y(self, test_only=False):
		if not test_only:
			#training data
			X_tr, y_tr = [], []
			for user in self.train_ids:
				if self.dataset.has_key(user):
					if self.dataset.get(user).has_key('class') and self.has_non_text_features(self.dataset[user]):
						X_tr.append(self.get_non_text_features(self.dataset[user]))
						y_tr.append(self.dataset[user]['class'])
			print
			print "train:", len(X_tr), len(y_tr)
			# testing data
			X_te, y_te = [], []
			for user in self.test_ids:
				if self.dataset.has_key(user):
					if self.dataset.get(user).has_key('class') and self.has_non_text_features(self.dataset[user]):
						X_te.append(self.get_non_text_features(self.dataset[user]))
						y_te.append(self.dataset[user]['class'])
			print				
			print "test:", len(X_te), len(y_te)
			return {'train': {'X': X_tr, 'y': y_tr}, 'test': {'X': X_te, 'y': y_te}}


	def initialize_data(self, test_only=False):
		X_y_dict = self.get_X_y(test_only)
		if not test_only:
			self.train_data = X_y_dict['train']
		self.test_data = X_y_dict['test']

	def train(self):
		self.clf = tree.DecisionTreeClassifier()
		self.clf = self.clf.fit(self.train_data['X'], self.train_data['y'])
		out = tree.export_graphviz(self.clf, out_file='decision_tree_dr.dot', feature_names=self.features)
		out.close()
	
	def prediction(self):
		y_predicted = self.clf.predict(self.test_data['X'])
		score = metrics.f1_score(self.test_data['y'], y_predicted)
		print "f1-score:   %0.3f" % score
		print "classification report:"
		print metrics.classification_report(self.test_data['y'], y_predicted, target_names=['democrats', 'republican'])

	def get_non_text_features(self, user_vector):
		fs = [user_vector['tcot'],
			  user_vector['syria'],
			  user_vector['p2'],
			  user_vector['bengahazi'],
			  user_vector['obama'],
			  user_vector['teaparty'],
			  user_vector['uniteblue'],
			  user_vector['gop'],
			  user_vector['obamacare'],
			  user_vector['tlot'],
			  user_vector['pjnet'],
			  user_vector['lnyhbt'],
			  user_vector['tgdn'],
			  user_vector['israel'],
			  user_vector['ccot'],
			  user_vector['romneyryan2012'],
			  user_vector['nra'],
			  user_vector['nsa'],
			  user_vector['irs']]
		return fs

	def has_non_text_features(self, user_vector):
		for f in self.features:
			if f not in user_vector:
				return False
		return True

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
		self.initialize_data(False)
		y_predicted = self.clf.predict(self.test_data['X'])
		#print y_predicted
		return y_predicted


def main():
	uc = UserClassifier("data/labelled_user_new.txt", 60)
	uc.initialize_data()
	uc.train()
	uc.prediction()
	#uc.cross_validate()

if __name__ == "__main__":
	main()

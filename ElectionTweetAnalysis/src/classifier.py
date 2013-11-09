'''
classifier.py
@author: Vandana Bachani
Classification of campaigners, supporters and neutral users from Election Tweets
'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn import metrics
from pymongo import Connection
import random

class UserClassifier:
	DB_SERVER = "localhost"
	DB_PORT = 27017
	DB_NAME = "election_analysis"
	COLLECTION_UV = "user_vector"
	def __init__(self, labelled_user_ids_file, train_percent):
		f = open(labelled_user_ids_file, 'r')
		self.data_ids = []
		num = f.readline()
		for line in f:
			line = line.split()
			self.data_ids.append(line[0])
		print self.data_ids
		random.shuffle(self.data_ids)

		num_ids = len(self.data_ids) * 1
		num_train = (train_percent/100.0) * num_ids
		self.train_ids = [self.data_ids[i].strip() for i in range(int(num_train))]
		#print self.train_ids
		self.test_ids = [self.data_ids[int(num_train+i)].strip() for i in range(int(num_ids - num_train))]
		#print self.test_ids
		self.features = ['polarity', 'statuses_count', 'election_tweet_count', 'friends_count', 'followers_count', 'listed_count', 'favourites_count', 'avg_num_retweets', 'num_retweets', 'num_retweets', 'mention_in_degree',	'mention_out_degree', 'var_interval', 'tweet_similarity', 'senti_score', 'status_variance']
		
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
			"""
			texts = []
			for i in user_vectors_train:
				texts.append(''.join(i['tweets']) + ' ' + i['description'] + ' ' + i['status'])
			self.vectorizer = TfidfVectorizer(min_df=5, max_features=10000, stop_words='english')
			X_train = self.vectorizer.fit_transform(texts)
			print 'num text features: ', len(self.vectorizer.get_feature_names())
			X_tr = X_train.toarray()
			"""
			X_tr, y_tr = [], []
			for i in user_vectors_train:
				X_tr.append(self.get_non_text_features(i))
				y_tr.append(i['class'])
				#print X_tr, y_tr

		#test data
		user_vectors_test = []
		for i in self.test_ids:
			it = self.db[self.COLLECTION_UV].find({'_id': i})
			for j in it:
				user_vectors_test.append(j)
		
		"""
		texts = []
		for i in user_vectors_test:
			texts.append(''.join(i['tweets']) + ' ' + i['description'] + ' ' + i['status'])
		X_test = self.vectorizer.transform(texts)
		X_te = X_test.toarray()
		"""
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
		self.clf = tree.DecisionTreeClassifier()
		self.clf = self.clf.fit(self.train_data['X'], self.train_data['y'])
		out = tree.export_graphviz(self.clf, out_file='decision_tree.dot', feature_names=self.features)
		out.close()
	
	def prediction(self):
		y_predicted = self.clf.predict(self.test_data['X'])
		score = metrics.f1_score(self.test_data['y'], y_predicted)
		print "f1-score:   %0.3f" % score
		print "classification report:"
		print metrics.classification_report(self.test_data['y'], y_predicted,
																				target_names=['campaigners', 'neutral'])

	def get_non_text_features(self, user_vector):
		fs = [(user_vector['polarity']['obama'] - user_vector['polarity']['romney'])**2,
						user_vector['statuses_count'],
						user_vector['election_tweet_count'],
						user_vector['friends_count'],
						user_vector['followers_count'],
						user_vector['listed_count'],
						user_vector['favourites_count'],
						user_vector['avg_num_retweets'],
						user_vector['num_retweets'],
						user_vector['mention_in_degree'],
						user_vector['mention_out_degree'],
						user_vector['var_interval'],
						user_vector['tweet_similarity'],
						#(user_vector['senti_score']/user_vector['election_tweet_count'])
						]
		if 'status_variance' in user_vector:
			fs.append(user_vector['status_variance'])
		else:
			fs.append(1)
		return fs

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
		#print y_predicted
		return y_predicted


def main():
	uc = UserClassifier('labelled_users_new.txt', 60)
	'''uc.initialize_data()
	uc.train()
	uc.prediction()'''
	uc.cross_validate()

	#test random
	ids_to_test = ["RyanfromJersey", "SASSIE163", "Streetglidin09", "StudSlayer", "Stupefix_", "StupidManWaka", "SuJuNevvs", "SuJu_Wifey", "SuSu4u12", "SuburbanLucy", "Succubus_aoi", "SuckkOnMyTweets", "Sudieyk3", "SueHM", "SugarCocaine_", "SujuFor_ELFindo", "SulledOut", "SultanAlQassemi", "SummerDepp", "Summer_Faery"]
	p = uc.test(ids_to_test)
	for i in range(len(p)):
		print ids_to_test[i], ": ",
		if p[i] == 0: print "Campaigner"
		else: print "Neutral"
		it = uc.db['user_vector'].find({'_id': ids_to_test[i]}, {'tweets': 'true'})
		for i in it:
			print i

if __name__ == "__main__":
	main()

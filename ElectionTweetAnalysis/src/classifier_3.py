'''
classifier_3.py
@author: Vandana Bachani, Bolun Huang
@add naive bayes classification on text feature
@in the database, class = 1, neutral; class = 0, campaigner/supporter
Classification of campaigners, supporters and neutral users from Election Tweets
'''
import cjson
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import GaussianNB
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
		self.ID_te = []
		#num = f.readline()
		count = 0
		count_2 = 0
		for line in f:
			line = line.split()
			if len(line) >= 2:
				if int(line[1]) > 15 and line[2] == 's':
					self.data_ids.append(line[0])
					count += 1
				elif int(line[1]) > 8 and line[2] == 'c':
					self.data_ids.append(line[0])
					count += 1
				elif int(line[1]) > 0 and line[2] == 'j':
					pass
					#self.data_ids.append(line[0])
				elif line[2] == 'n':
					self.data_ids.append(line[0])
					count_2 += 1
		print count, count_2
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
		
		self.features = ['polarity',
						'tag_polarity',
						#'tag_count',
						#'statuses_count',
						#'election_tweet_count',
						'following_follower_ratio',
						#'friends_count',
						#'followers_count',
						#'listed_count',
						#'favourites_count',
						'avg_num_retweets',
						#'num_retweets', 
						#'mention_in_degree',
						#'mention_out_degree',
						#'var_interval',
						#'avg_interval',
						'tweet_similarity',
						'sentiment_abortion',
						#'sentiment_obamacare',
						#'sentiment_guncontrol',
						#'sentiment_immigration',
						'sentiment_edu',
						'sentiment_military',
						'sentiment_economic',
						'sentiment_bengahzi',
						#'sentiment_chrysler',
						#'sentiment_fraud',
						'sentiment_obama',
						'sentiment_romney',
						'topic_sentiment', ## combination of all above sentiments
						'url_percentage',
						'senti_score',
						#'status_variance'
						]
		'''
		self.features = ['polarity',
						'tag_polarity',
						#'tag_count',
						#'statuses_count',
						#'election_tweet_count',
						'following_follower_ratio',
						#'friends_count',
						#'followers_count',
						#'listed_count',
						#'favourites_count',
						'avg_num_retweets',
						#'num_retweets', 
						#'mention_in_degree',
						#'mention_out_degree',
						#'var_interval',
						#'avg_interval',
						'tweet_similarity',
						'sentiment_abortion',
						'sentiment_obamacare',
						#'sentiment_guncontrol',
						#'sentiment_immigration',
						'sentiment_edu',
						'sentiment_military',
						'sentiment_economic',
						'sentiment_bengahzi',
						'sentiment_chrysler',
						'sentiment_fraud',
						'sentiment_obama',
						'sentiment_romney',
						'topic_sentiment', ## combination of all above sentiments
						'url_percentage',
						'senti_score',
						#'status_variance'
						]
		'''

		
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
			
			texts = []
			try:
				for i in user_vectors_train:
					texts.append(''.join(i['tweets']) + ' ' + i['description'])
			except:
				print i['_id']
				#exit(0)
			## TFIDF text feature extraction ###
			self.vectorizer = TfidfVectorizer(min_df=1, max_features=1000, stop_words='english')
			X_train = self.vectorizer.fit_transform(texts)
			print 'num text features: ', len(self.vectorizer.get_feature_names())
			X_tr = X_train.toarray()
			y_tr = []
			for i in user_vectors_train:
				#X_tr.append(self.get_non_text_features(i))
				try:
					y_tr.append(i['new_class'])
				except:
					print i['_id']
				#print X_tr, y_tr

		#test data
		user_vectors_test = []
		for i in self.test_ids:
			it = self.db[self.COLLECTION_UV].find({'_id': i})
			for j in it:
				user_vectors_test.append(j)
		
		
		texts = []
		for i in user_vectors_test:
			texts.append(''.join(i['tweets']) + ' ' + i['description'])
		X_test = self.vectorizer.transform(texts)
		X_te = X_test.toarray()
		
		y_te = []
		for i in user_vectors_test:
			self.ID_te.append(i['_id'])
			#X_te.append(self.get_non_text_features(i))
			if(not test_only):
				y_te.append(i['new_class'])
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
		#self.clf = tree.DecisionTreeClassifier()
		#self.clf = self.clf.fit(self.train_data['X'], self.train_data['y'])
		#out = tree.export_graphviz(self.clf, out_file='data/decision_tree.dot', feature_names=self.features)
		#out.close()
		### naive bayes model
		self.clf_2 = GaussianNB()
		self.clf_2.fit(self.train_data['X'], self.train_data['y'])
	
	def prediction(self):
		print "**************naive bayes model*****************"
		y_predicted = self.clf_2.predict(self.test_data['X'])
		y_predicted_prob = self.clf_2.predict_proba(self.test_data['X'])
		score = metrics.f1_score(self.test_data['y'], y_predicted)
		print "f1-score:   %0.3f" % score
		print self.ID_te
		for i in range(0, len(self.test_data['y'])):
			print self.test_data['y'][i],
		print '\t'
		for i in range(0, len(y_predicted)):
			print y_predicted[i],
		print '\t'
		#for i in range(0, len(y_predicted_prob)):
		#	print y_predicted_prob[i],
		#print '\t'
		for i in range(0, len(self.test_data['y'])):
			if self.test_data['y'][i] != y_predicted[i]:
				print self.ID_te[i], self.test_data['y'][i], y_predicted_prob[i]
		print '\t'
		print "classification report:"
		print metrics.classification_report(self.test_data['y'], y_predicted, target_names=['campaigners','neutral'])
		#print metrics.classification_report(self.test_data['y'], y_predicted, target_names=['other', 'journalist',''])
	def get_non_text_features(self, user_vector):
		try:
			fs = [(user_vector['polarity']['obama'] - user_vector['polarity']['romney'])**2,
						user_vector['tag_polarity'],
						#user_vector['tag_count'],
						#user_vector['statuses_count'],
						#user_vector['election_tweet_count'],
						user_vector['following_follower_ratio'],
						#user_vector['friends_count'],
						#user_vector['followers_count'],
						#user_vector['listed_count'],
						#user_vector['favourites_count'],
						user_vector['avg_num_retweets'],
						#user_vector['num_retweets'],
						#user_vector['mention_in_degree'],
						#user_vector['mention_out_degree'],
						#user_vector['var_interval'],
						#user_vector['avg_interval'],
						user_vector['tweet_similarity'],
						user_vector['sentiment_abortion'],
						#user_vector['sentiment_obamacare'],
						#user_vector['sentiment_guncontrol'],
						#user_vector['sentiment_immigration'],
						user_vector['sentiment_edu'],
						user_vector['sentiment_military'],
						user_vector['sentiment_economic'],
						user_vector['sentiment_bengahzi'],
						#user_vector['sentiment_chrysler'],
						#user_vector['sentiment_fraud'],
						user_vector['sentiment_obama'],
						user_vector['sentiment_romney'],
						user_vector['topic_sentiment'],
						user_vector['url_percentage'],
						(user_vector['senti_score']/user_vector['election_tweet_count'])
						]
		except:
			pass
		'''
		fs = [(user_vector['polarity']['obama'] - user_vector['polarity']['romney'])**2,
						user_vector['tag_polarity'],
						#user_vector['tag_count'],
						#user_vector['statuses_count'],
						#user_vector['election_tweet_count'],
						user_vector['following_follower_ratio'],
						#user_vector['friends_count'],
						#user_vector['followers_count'],
						#user_vector['listed_count'],
						#user_vector['favourites_count'],
						user_vector['avg_num_retweets'],
						#user_vector['num_retweets'],
						#user_vector['mention_in_degree'],
						#user_vector['mention_out_degree'],
						#user_vector['var_interval'],
						#user_vector['avg_interval'],
						user_vector['tweet_similarity'],
						user_vector['sentiment_abortion'],
						user_vector['sentiment_obamacare'],
						#user_vector['sentiment_guncontrol'],
						#user_vector['sentiment_immigration'],
						user_vector['sentiment_edu'],
						user_vector['sentiment_military'],
						user_vector['sentiment_economic'],
						user_vector['sentiment_bengahzi'],
						user_vector['sentiment_chrysler'],
						user_vector['sentiment_fraud'],
						user_vector['sentiment_obama'],
						user_vector['sentiment_romney'],
						user_vector['topic_sentiment'],
						user_vector['url_percentage'],
						(user_vector['senti_score']/user_vector['election_tweet_count'])
						]
		'''
		#if 'status_variance' in user_vector:
		#	fs.append(user_vector['status_variance'])
		#else:
		#	fs.append(1)
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
			self.vectorizer = TfidfVectorizer(min_df=1, max_features=1000, stop_words='english')
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
		#print y_predicted
		return y_predicted


def main():
	uc = UserClassifier('user_data/labelled_new.txt', 75)
	uc.initialize_data()
	uc.train()
	uc.prediction()
	#uc.cross_validate()

	#test random
	#ids_to_test = ["RyanfromJersey", "SASSIE163", "Streetglidin09", "StudSlayer", "Stupefix_", "StupidManWaka", "SuJuNevvs", "SuJu_Wifey", "SuSu4u12", "SuburbanLucy", "Succubus_aoi", "SuckkOnMyTweets", "Sudieyk3", "SueHM", "SugarCocaine_", "SujuFor_ELFindo", "SulledOut", "SultanAlQassemi", "SummerDepp", "Summer_Faery"]
	#p = uc.test(ids_to_test)
	'''
	for i in range(len(p)):
		print ids_to_test[i], ": ",
		if p[i] == 0: print "Campaigner"
		else: print "Neutral"
		it = uc.db['user_vector'].find({'_id': ids_to_test[i]}, {'tweets': 'true'})
		for i in it:
			print i
	'''
if __name__ == "__main__":
	main()

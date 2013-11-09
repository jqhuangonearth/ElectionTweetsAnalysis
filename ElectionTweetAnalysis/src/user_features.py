'''
user_features.py
@author: Vandana Bachani
Extract and store user features.
trying to collect the following features from the tweets and user_profile data
election_tweet_count, num_tweets_obama, num_tweets_romney, sentiment_value, urls, urls_affiliation, latest_tweet_variation_in_content,  relation_with_major_players
'''
from __future__ import division
from pymongo import Connection
import cjson

class UserFeatures:
	DB_SERVER = "localhost" 
	DB_PORT = 27017
	DB_NAME = "election_analysis"
	COLLECTION_UV = "user_vector"
	COLLECTION_UP = "user_profiles"
	MAJOR_ACCOUNTS = ['@TeamObama']
	def __init__(self, tweets_count_file):
		#<user_name,tweets_count> key value pairs
		self.tweet_counts = {}
		self.user_ids = []
		f = open(tweets_count_file, 'r')
		lines = f.readlines()
		for i in lines:
			data = i.strip().split()
			self.tweet_counts[data[0]] = int(data[1])
			self.user_ids.append(data[0])
		f.close()
		self.connection = Connection(self.DB_SERVER, self.DB_PORT)
		self.db = self.connection[self.DB_NAME]
	
	def create_n_store_user_vectors(self):
		for i in self.user_ids:
			user_obj = self.create_user_object(i)
			if user_obj != None:
				self.db[self.COLLECTION_UV].insert(user_obj)

	def create_user_object(self, user_id):
		user, user_profile_object = {}, None
		user['_id'] = user_id
		it = self.get_user_profile_object(user_id)
		for i in it:
			user_profile_object = i
		if user_profile_object == None:
			return None
		user['election_tweet_count'] = self.tweet_counts[user_id]
		tweets_info = self.get_tweets_info(user_id)
		user['tweets'] = tweets_info['tweets']
		user['favouring_tweet_count'] = tweets_info['favouring_tweet_count']
		user['polarity'] = tweets_info['polarity']
		user['num_retweets'] = tweets_info['retweets']
		user['avg_num_retweets'] = tweets_info['avg_num_retweets']
		#user['avg_sentiment_value'] = tweets_info['avg_sentiment_value']

		user['description'] = user_profile_object['description']
		#might not be useful
		user['statuses_count'] = user_profile_object['statuses_count']
		user['friends_count'] = user_profile_object['friends_count']
		user['followers_count'] = user_profile_object['followers_count']
		user['favourites_count'] = user_profile_object['favourites_count']
		user['listed_count'] = user_profile_object['listed_count']
		if 'status' in user_profile_object:
			user['status'] = user_profile_object['status']['text']
			if is_election_related(user['status']):
				user['status_variance'] = 0
			else:
				user['status_variance'] = 1
		#time of status or account creation might not be helpful

		#fill in fields from user profile features
		#urls, url_affiliation, latest_tweet_variation

		#lists campaigners as friends?
		#user['relation_with_major_players'] = [] #0/1 relation whether follows or not
		return user
	
	def get_tweets_info(self, user_id):
		tweets_file = '/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json' % user_id
		total, rt_from, avg_n_rts = 0, 0, 0
		obama_keywords = ['obama', 'democrat', 'biden']
		romney_keywords = ['romney', 'paul ryan', 'republican', 'mitt']
		tweets_info = {}
		count_map = {'obama': 0.0, 'romney': 0.0}
		tweets = []
		
		f = open(tweets_file, 'r')
		lines = f.readlines()
		for l in lines:
			data = cjson.decode(l)
			if 'tx' in data:
				tweets.append(data['tx'])
			else:
				tweets.append(data[':x'])
			for ow in obama_keywords:
				if 'tx' in data:
					if ow in data['tx'].lower():
						count_map['obama'] += 1
						break
				else:
					if ow in data[':x'].lower():
						count_map['obama'] += 1
						break
			for rw in romney_keywords:
				if 'tx' in data:
					if rw in data['tx'].lower():
						count_map['romney'] += 1
						break
				else:
					if rw in data[':x'].lower():
						count_map['romney'] += 1
						break
			if 'rt_from' in data:
				rt_from += 1
			avg_n_rts += data['n_rts']
			total += 1
		total *= 1.0
		tweets_info['tweets'] = tweets
		tweets_info['avg_num_retweets'] = avg_n_rts/total
		tweets_info['retweets'] = rt_from
		tweets_info['favouring_tweet_count'] = count_map
		tweets_info['polarity'] = {'obama': (count_map['obama']/total), 'romney': count_map['romney']/total}
		#tweets_info['avg_sentiment_value']
		return tweets_info
	
	def get_tweet_sentiment_value(self, user_id, user_tweets):
		#alchemy api call
		pass

	def get_user_profile_object(self, user_id):
		p = self.db[self.COLLECTION_UP].find({'_id': user_id})
		return p

def is_election_related(text):
	f = open('filter_list.txt', 'r')
	words = [x.strip() for x in f.readlines()]
	for w in words:
		if w in text.lower():
			return True
	return False

if __name__ == "__main__":
 uv = UserFeatures('high_vol_tweeters')
 uv.create_n_store_user_vectors()

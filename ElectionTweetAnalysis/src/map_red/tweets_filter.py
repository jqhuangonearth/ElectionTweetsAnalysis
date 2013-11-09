'''
tweets_filter.py
@author: Vandana Bachani
Module to filter election tweets from the available tweets.
'''

from library.mrjobwrapper import ModifiedMRJob
import cjson

class FilterElectionTweets(ModifiedMRJob):

	def configure_options(self):
		super(FilterElectionTweets, self).configure_options()
		self.add_file_option('--keywords', default='filter_list.txt')
	
	def __init__(self, *args, **kwargs):
		super(FilterElectionTweets, self).__init__(*args, **kwargs)
		self.keywords = [x.strip() for x in open(self.options.keywords, 'r').readlines()]
	
	def mapper(self, key, line):
		data = cjson.decode(line)
		if 'delete' in data:
			return
		if data['text'] == None:
			return
		fields = [data['text']]
		htag_list = []
		url_list = []
		for i in data['entities']['hashtags']:
			fields.append(i['text'])
			htag_list.append(i['text'])
		for i in data['entities']['urls']:
			fields.append(i['expanded_url'])
			url_list.append(i['expanded_url'])
		is_election = self.is_election_tweet(fields)
		if is_election != None:
			tweet = {'tx': data['text'], 'id': data['id'], 'h': htag_list, 'urls': url_list, 'reply_to': data['in_reply_to_screen_name'], 'n_rts': data['retweet_count'], 'u': {'id': data['user']['id'], 'l': data['user']['location'], 'd': data['user']['description'], 'n_friends': data['user']['friends_count'], 'sn': data['user']['screen_name']}, 'geo': data['coordinates'], 't': data['created_at']}
			if 'retweeted_status' in data:
				tweet['rt_from'] = {'sn': data['retweeted_status']['user']['screen_name'], 'id': data['retweeted_status']['id']}
			yield is_election, tweet
	
	def is_election_tweet(self, fields):
		for i in fields:
			if i == None:
				continue
			field = i.lower()
			for k in self.keywords:
				if k in field:
					return k
		return None

if __name__ == '__main__':
	FilterElectionTweets.run()

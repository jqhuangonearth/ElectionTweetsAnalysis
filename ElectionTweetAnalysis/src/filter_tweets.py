'''
filter_tweets.py
@author: Vandana Bachani
Module to filter election tweets from the available tweets.
'''

from datetime import datetime
from dateutil.relativedelta import relativedelta
import cjson, os, gzip, sys

class FilterElectionTweets():
	def __init__(self, filter_list, outfile):
		self.keywords = [x.strip() for x in open(filter_list, 'r').readlines()]
		self.outfile = open(outfile, 'w')
			
	def get_election_tweet(self, raw_tweet):
		try:
			data = cjson.decode(raw_tweet)
			if 'delete' in data:
				return None
			if data['text'] == None:
				return None
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
				self.outfile.write(cjson.encode(tweet)+'\n')
				return tweet
			else:
				return None
		except:
			return None
	
	def is_election_tweet(self, fields):
		for i in fields:
			if i == None:
				continue
			field = i.lower()
			for k in self.keywords:
				if k in field:
					return k
		return None

def dated_input_files_iterator(startTime, endTime, input_folder):
	current = startTime
	while current <= endTime:
		input_dir = input_folder + '%s/%s/' % (current.month, current.day)
		for root, _, files in os.walk(input_dir):
			for i in files:
				yield root+i
		current += relativedelta(days=1)

def main():
	output_file = os.path.expanduser('~/ElectionTweetsAnalysis/data/%s/') % 'results/filter' + 'tweets'
	input_folder = '/mnt/chevron/bde/Data/TweetData/SampleTweets/2012/'
	fet = FilterElectionTweets('filter_list.txt', output_file)
	it = dated_input_files_iterator(datetime(2012, 10, 1), datetime(2012, 11, 6), input_folder)
	for i in it:
		f = gzip.open(i, 'rb')
		lines = f.readlines()
		for j in lines:
			fet.get_election_tweet(j)

if __name__ == '__main__':
	sys.exit(main())

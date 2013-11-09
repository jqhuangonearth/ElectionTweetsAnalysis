'''
filtermr.py
@author: Vandana Bachani
Map Reduce job starter for filtering election tweets.
'''

from datetime import datetime
from library.mrjobwrapper import runMRJob
from tweets_filter import FilterElectionTweets
import os
from dateutil.relativedelta import relativedelta

class FilterElectionTweetsMRJobRunner(object):

	@staticmethod
	def filter_tweets(input_files_start_time, input_files_end_time):
		mr_class = FilterElectionTweets
		output_file = os.path.expanduser('~/ElectionTweetsAnalysis/data/%s/') % 'results/filter' + 'tweets'
		input_folder = '/mnt/chevron/bde/Data/TweetData/SampleTweets/2012/'
		runMRJob(mr_class,
							output_file,
							FilterElectionTweetsMRJobRunner.get_dated_input_files(input_files_start_time, input_files_end_time, input_folder),
							mrJobClassParams = {'job_id': 'as'},
							#args = [],
							jobconf = {'map.reduce.tasks': 300}
		)

	@staticmethod
	def run():
		input_files_start_time, input_files_end_time = \
									datetime(2012, 10, 1), datetime(2012, 11, 6)
		FilterElectionTweetsMRJobRunner.filter_tweets(input_files_start_time,
																									input_files_end_time)
	
	@staticmethod
	def get_dated_input_files(startTime, endTime, input_folder):
		current = startTime
		while current <= endTime:
			input_dir = input_folder + '%s/%s/' % (current.month, current.day)
			for root, _, files in os.walk(input_dir):
				for i in files:
					yield root+i
			current += relativedelta(days=1)

if __name__ == '__main__':
	FilterElectionTweetsMRJobRunner.run()

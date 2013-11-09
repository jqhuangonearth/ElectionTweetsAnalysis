import cjson
import os
import httplib2
import urllib
import random
from pymongo import Connection
import matplotlib.pyplot as plt
import re

"""
APIKEY = 'c8231ecbb8f6dbe91199d3318a6a604ac24e5da9'

http = httplib2.Http()

text = 'I hate Obama and I love Romney'
query = 'http://access.alchemyapi.com/calls/text/TextGetTextSentiment?apikey={0}&text={1}&outputMode=json'.format(urllib.quote_plus(APIKEY), urllib.quote_plus(text))
(header, content) = http.request(query, 'GET')
if header['status'] == '200':
	print content
else:
	print header
"""

def get_sentiment():
	APIKEY = urllib.quote_plus('c8231ecbb8f6dbe91199d3318a6a604ac24e5da9')
	http = httplib2.Http()
	DBSERVER = "localhost"
	DBPORT = 27017
	DBNAME = "election_analysis"
	conn = Connection(DBSERVER, DBPORT)
	db = conn[DBNAME]
	f = open("user_data/labelled_new_into_db.txt", 'r')
	dic = {}
	for line in f:
		line = line.split()
		if len(line) == 4:
			dic.update({line[0]: line[2]})
		else:
			dic.update({line[0]: ''})
	print dic
	f.close()
	#f2 = open("topic_sentimantic.txt", "w")
	f3 = open("data/topic_military_sentimantic_2.txt", "w")
	#f2.write('{} '.format('username').ljust(20)+'{} '.format('type').ljust(10)+'{} '.format('sen_score').ljust(10)+'{} '.format('sen_type').ljust(10)+'tweet\n')
	tweet_count_2 = 0
	for u in dic:
		it = db['user_vector'].find({'_id': u})
		sen_avg_score = 0
		for i in it:
			tweets = i['tweets']
			#i['sentiments'] = []
			#i['senti_score'] = 0
			tweet_count = 0
			sen_score_sum = 0
			for t in tweets:
				try:
					t = t.lower()
					#print '1 ',t
					#t = re.sub(r'@[a-zA-Z0-9_:]*\s', '', t)
					#t = re.sub(r'@[a-zA-Z0-9_:]*\b', '', t)
					#t = re.sub(r'#[a-zA-Z0-9]*\s', '', t)
					#print '2 ',t
					#continue
					'''
					liar lie etc. to see who is 
					'''
					#if ('obama' in t or 'biden' in t or 'democrat' in t) and not ('romne' in t or 'mitt' in t or 'ryan' in t or 'republican' in t or 'gop' in t):
					#	t = re.sub(r'\b%s\b' %('obama'), '', t)
					#	t = re.sub(r'\b%s\b' %('biden'), '', t)
					#	t = re.sub(r'\b%s\b' %('democrat'), '', t)
					#	t = re.sub(r'\b%s\b' %('romney'), '', t)
					#	t = re.sub(r'\b%s\b' %('mitt'), '', t)
					#	t = re.sub(r'\b%s\b' %('ryan'), '', t)
					#	t = re.sub(r'\b%s\b' %('republican'), '', t)
					#	t = re.sub(r'\b%s\b' %('gop'), '', t)
					#if 'bengahzi' in t or 'benghazi' in t or 'bengahazi' in t:
					#if 'sensata' in t or 'chrysler' in t or 'jeep' in t or 'gm' in t or 'motor' in t or 'car' in t:
					#if 'business' in t or 'economy' in t or 'economic' in t or 'debt' in t or 'deficit' in t or 'labor' in t or 'worker' in t or 'job' in t or 'capital' in t or 'budget' in t or 'employment' in t or 'middle class' in t or 'middleclass' in t or 'tax' in t:
					if 'military' in t or 'iraq' in t or 'iran' in t or 'war' in t or 'syria' in t or 'israel' in t:
					#if 'immigration' in t or 'immigrant' in t or 'law' in t or 'federal' in t or 'employ' in t or 'genetic' in t:
					#if 'edu' in t or 'child' in t or 'college' in t or 'student' in t or 'kid' in t or 'teacher' in t:
					#if 'abortion' in t or 'pregnant' in t or 'pregnancy' in t or 'women' in t or 'woman' in t:
					#if 'obamacare' in t or 'obama care' in t or 'healthcare' in t or 'health care' in t or 'medic' in t:
					#if 'gun' in t or 'crime' in t or 'criminal' in t or 'security' in t:
					#if 'gay' in t:
					#if 'steal' in t or 'fraud' in t or 'lie' in t or 'liar' in t:
						tweet_count = tweet_count + 1
						tweet_count_2 = tweet_count_2 + 1
						#break
						query = 'http://access.alchemyapi.com/calls/text/TextGetTextSentiment?apikey={0}&text={1}&outputMode=json'.format(APIKEY, urllib.quote_plus(t.encode('utf8')))
						(header, content) = http.request(query, 'GET')
						#h = cjson.decode(header)
						#print h
						if header and header['status'] == '200':
							s = cjson.decode(content)
							print s
							if s['status'] == 'OK':
								#i['sentiments'].append(s['docSentiment'])
								if s['docSentiment']['type'] == 'neutral':
									pass
									#f2.write('{} '.format(i['_id']).ljust(20)+'{} '.format(dic[u]).ljust(10)+'{} '.format(str(0)).ljust(10)+'{} '.format(s['docSentiment']['type']).ljust(10)+t+'\n')
								else:
									#if s['docSentiment']['type'] == 'negative':
									#	score = float(s['docSentiment']['score'])*(-1.0)
									#else:
									score = float(s['docSentiment']['score'])
									sen_score_sum = sen_score_sum + float(score)
									#print sen_score_sum
									#f2.write('{} '.format(i['_id']).ljust(20)+'{} '.format(dic[u]).ljust(20)+'{} '.format(s['docSentiment']['score']).ljust(10)+'{} '.format(s['docSentiment']['type']).ljust(10)+t+'\n')
							else:
								print i['_id'], s
						else:
							pass
				except:
					raise
			'''
			if not tweet_count == 0:
				sen_avg_score = sen_score_sum/float(tweet_count) ### take an average
				f3.write('{} '.format(i['_id']).ljust(20)+'{} '.format(dic[u]).ljust(20)+'{} '.format(str(sen_score_sum)).ljust(10)+str(sen_avg_score)+'\n')
			else: ### if they have no tweet on the topic, see them as neutral ###
				f3.write('{} '.format(i['_id']).ljust(20)+'{} '.format(dic[u]).ljust(20)+'{} '.format(str(0)).ljust(10)+str(0)+'\n')
					#continue
				#db['user_vector'].update({'_id': i['_id']}, i, upsert=False)
			'''
	#f2.close()
	print tweet_count_2
	f3.close()
	
def draw():
	f3 = open("data/topic_military_sentimantic_2.txt", "r")
	for line in f3:
		line = line.split()
		if line[1] == 'c':
			#for t in self.dic[user][5]:
			plt.plot(float(line[2]), random.random(), 'ro')
		elif line[1] == 's':
			#for t in self.dic[user][5]:
			plt.plot(float(line[2]), random.random(), 'yo')
		elif line[1] == 'n':
			plt.plot(float(line[2]), random.random(), 'bo')
		#else:
		#	plt.plot(float(line[2]), random.random(), 'go')
	f3.close()
	plt.show()
	
def create_user_tweet_files(output_base_dir, tweets_file):
	if not os.path.exists(output_base_dir):
		os.umask(0)
		os.makedirs(output_base_dir, 0777)
	user_tweet_map = {}
	f = open(tweets_file, 'r')
	for l in f:
		data = cjson.decode(l)
		sn = data['u']['sn']
		if sn in user_tweet_map:
			user_tweet_map[sn].append(data)
		else:
			user_tweet_map[sn] = [data]
	f.close()
	for x in user_tweet_map:
		if len(user_tweet_map[x]) < 3:
			continue
		fname = output_base_dir + '%s.json' % x
		f1 = open(fname, 'w')
		for data in user_tweet_map[x]:
			f1.write(cjson.encode(data)+'\n')
		f1.close()

def main():
	get_sentiment()
	#draw()

if __name__ == "__main__":
	main()
	
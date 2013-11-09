import cjson
import os
import httplib2
import urllib
from pymongo import Connection

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
	APIKEY = 'c8231ecbb8f6dbe91199d3318a6a604ac24e5da9'
	http = httplib2.Http()
	DBSERVER = "localhost"
	DBPORT = 27017
	DBNAME = "election_analysis"
	conn = Connection(DBSERVER, DBPORT)
	db = conn[DBNAME]
	f = open("user_data/labelled_new_into_db.txt", 'r')
	f2 = open("user_data/labelled_users.txt",'r')
	users = []
	already_labelled = []
	for x in f:
		x = x.strip()
		x = x.split()
		users.append(x[0])
	for y in f2:
		y = y.strip()
		already_labelled.append(y)
	f.close()
	f2.close()	
	for u in users:
		if not u in already_labelled:
			it = db['user_vector'].find({'_id': u})
			for i in it:
				tweets = i['tweets']
				i['sentiments'] = []
				i['senti_score'] = 0
				for t in tweets:
					try:
						query = 'http://access.alchemyapi.com/calls/text/TextGetTextSentiment?apikey={0}&text={1}&outputMode=json'.format(urllib.quote_plus(APIKEY), urllib.quote_plus(t.encode('utf8')))
						(header, content) = http.request(query, 'GET')
						if header['status'] == '200':
							s = cjson.decode(content)
							print s
							if s['status'] == 'OK':
								i['sentiments'].append(s['docSentiment'])
								if s['docSentiment']['type'] == 'neutral': continue
								else:
									if s['docSentiment']['type'] == 'negative': s['docSentiment']['score'] = float(s['docSentiment']['score'])*(-1)
									i['senti_score'] += float(s['docSentiment']['score'])
						else:
							print header
					except:
						continue
				db['user_vector'].update({'_id': i['_id']}, i, upsert=False)
				

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

if __name__ == "__main__":
	get_sentiment()
	#pass
	#create_user_tweet_files('../data/results/user_tweets/', '../data/results/filter/tweets')

'''
Created on Nov 16, 2012

@author: vandana
Gets user_profiles from twitter user lookup api.
'''
import cjson
import httplib2
import sys
import time
import urllib
from utilities.twitter_request_session import RequestSession
from pymongo import Connection

class UserProfile:
  USER_LOOKUP_URL = 'http://api.twitter.com/1/users/lookup.json?' + \
      'screen_name={0}&include_entities=true'
  HTTP = httplib2.Http()
  @staticmethod
  def crawl(ids_file, output_file):
    f = open(ids_file, 'r')
    user_ids = [x.strip() for x in f.readlines()]
    f.close()
    f = open(output_file, 'w')
    c = 0
    num_userids = len(user_ids)
    request_ids = []
    rs = RequestSession()
    rs.start_session()
    for i in user_ids:
      request_ids.append(i)
      c += 1
      num_userids -= 1
      if c == 100 or num_userids == 0:
        rs.monitor_requests()
        response = UserProfile.lookup_user(request_ids)
        if response == None:
          print "error occurred. request cannot be completed."
          return
        print "processing response: ", rs.num_requests
        for profile in response:
          f.write(cjson.encode(profile)+'\n')
        request_ids = []
        c = 0
  
  @staticmethod
  def lookup_user(request_ids_list):
    str_ids_list = ','.join(request_ids_list)
    request_url = UserProfile.USER_LOOKUP_URL.format(urllib.quote_plus(str_ids_list))
    while True:
      response, content = UserProfile.HTTP.request(request_url, 'GET')
      try:
        if response['status'] == '200':
          #print content
          return cjson.decode(content)
        elif response['status'] == '400':
          print "request monitoring not working..."
          print "response: ", response
          time.sleep(60*60) #sleep for 60 mins before continuing
        elif response['status'] == '502':
          time.sleep(120) #sleep for 2 mins server is busy
        else:
          print "error occurred. no response"
          print "response: ", response
          print "response content: ", content
          return
      except:
        return

def reduced_user_profile(input_file, output_file):
	f = open(input_file, 'r')
	f1 = open(output_file, 'w')
	for l in f:
		data = cjson.decode(l)
		towrite = {
			'followers_count': data['followers_count'],
			'location': data['location'],
			'statuses_count': data['statuses_count'],
			'description': data['description'],
			'friends_count': data['friends_count'],
			'screen_name': data['screen_name'],
			'favourites_count': data['favourites_count'],
			'name': data['name'],
			'url': data['url'],
			'created_at': data['created_at'],
			'listed_count': data['listed_count'],
			'id': data['id']
		}
		if 'status' in data:
			towrite['status'] = {'text':data['status']['text'],
				'created_at': data['status']['created_at'],
				'in_reply_to_screen_name': data['status']['in_reply_to_screen_name'],
				'entities': {'urls': [x['expanded_url'] for x in data['status']['entities']['urls']], 'hashtags': data['status']['entities']['hashtags'], 'user_mentions': [x['screen_name'] for x in data['status']['entities']['user_mentions']]},
				'retweet_count': data['status']['retweet_count']
			}
		f1.write(cjson.encode(towrite)+'\n')
	f1.close()
	f.close()

def write_profiles_to_db(filename):
	f = open(filename, 'r')
	conn = Connection('localhost', 27017)
	db = conn['election_analysis']
	for l in f:
		data = cjson.decode(l)
		data['_id'] = data['screen_name']
		db['user_profiles'].insert(data)
	f.close()
        
def main():
	"""
  if len(sys.argv) < 2:
    UserProfile.crawl('user_ids.txt', 'user_profiles.txt')
  elif len(sys.argv) == 2:
    UserProfile.crawl(sys.argv[1], 'user_profiles.txt')
  else:
    UserProfile.crawl(sys.argv[1], sys.argv[2])
	"""
	"""
	reduced_user_profile('user_profiles.txt', 'user_profiles_shortened.txt')
	"""
	#write profiles to db
	write_profiles_to_db('user_profiles_shortened.txt')

if __name__ == "__main__":
  sys.exit(main())

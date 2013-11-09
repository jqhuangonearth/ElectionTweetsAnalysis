import ata
import cjson
import json
APP_CONSUMER_KEY = "K5ght1jy6fI1w8mpUCeiQ"
APP_CONSUMER_SECRET = "TdXtIb5upWPuLoFAJFWjalhmIgqcoZLNvw1IaTWTGS4"
ACCESS_TOKEN = "1260900631-3N7q5aSs9FgJxC3gwML0aRkQWiB4bTxuXzUYvjI"
ACCESS_SECRET = "x0DsZIvOX08AIwPLev4KyphulqI9n7HphlT0BDnYI"

def read_user_ids(filename):
    in_file = open(filename, 'r')
    lines = in_file.readlines()
    in_file.close()
    user_ids = []
    for line in lines:
        line = line.split()
        user_ids.append(int(line[1].strip()))
    return user_ids

def get_user_tweets(users):
    access_twitter_api = ata.Main(APP_CONSUMER_KEY, APP_CONSUMER_SECRET)
    users = users
    #print users
    user_tweets = []
    # "https://api.twitter.com/1/statuses/user_timeline.json?include_entities=true&include_rts=true&screen_name=username&count=5"
    URL = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    for i in range(len(users)):
        params = "include_entities=true&include_rts=true&user_id=%s&count=200" %(str(users[i]))
        content = access_twitter_api.request(URL,
                                             params,
                                             ACCESS_TOKEN, ACCESS_SECRET,
                                             sleep_rate_limit_exhausted="False")
        if content:
            content = cjson.decode(content)
            user_tweets.extend(content)
            print "Crawled user tweets: %d" %(users[i])
            #print content
    return user_tweets

def output_user_files(user_profiles, filename):
    out_file = open(filename, 'w')
    for user_profile in user_profiles:
        json.dump(user_profile, out_file)
        out_file.write("\n")
    out_file.close()

def main():
    users = []
    users = read_user_ids("user_withId_list.txt")
    user_tweets = []
    user_tweets = get_user_tweets(users)
    output_user_files(user_tweets, "user_data/user_tweets.json")

if __name__ == "__main__":
    main()

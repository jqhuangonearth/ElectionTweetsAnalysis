import ata
import cjson
import json

APP_CONSUMER_KEY = "RNej5qSVNkTTceUaxyG19Q"
APP_CONSUMER_SECRET = "m5Wp1GGsPacu37csncPBT0Na7eRHum7PLgzkG43qMco"
ACCESS_TOKEN = "1260900631-IlNMVWm9niq93X4qQMoUqnR1eKKJqxsrnX9lmzg"
ACCESS_SECRET = "jxL04WdoREZm4NWYYX5KzcF7mz1M9ugpr5AHclKXYk"

def read_user_ids(filename):
    in_file = open(filename, 'r')
    lines = in_file.readlines()
    in_file.close()
    user_ids = []
    for line in lines:
        line = line.split()
        user_ids.append(int(line[1].strip()))
    return user_ids

def get_user_followers(users):
    access_twitter_api = ata.Main(APP_CONSUMER_KEY, APP_CONSUMER_SECRET)
    users = users
    f_write = open("../user_data/user_followers.json","w")
    f_failed = open("failed_trails/userList_crawlfollowers.txt","w")
    # https://api.twitter.com/1.1/friends/ids.json?cursor=-1&screen_name=sitestreams&count=5000
    URL = "https://api.twitter.com/1.1/followers/ids.json"
    for i in range(len(users)):
        dict_followers = {}
        list_followers = []
        cursor = -1
        while cursor != 0:
            params = "cursor=%s&user_id=%s&count=5000" %(str(cursor), str(users[i]))
            try:
                content = access_twitter_api.request(URL,
                                                     params,
                                                     ACCESS_TOKEN, ACCESS_SECRET,
                                                     sleep_rate_limit_exhausted="False")
                if content:
                    content = cjson.decode(content)
                    list_followers.extend(content['ids'])
                    print "Crawled user followers with cursor %d: %d" %(cursor, users[i])
                    cursor = content['next_cursor']
            except:
                print "Failed at crawling user followers: %d" %(users[i])
                f_failed.write(str(users[i])+"\n")
                break
        if len(list_followers) != 0:
            dict_followers.update({str(users[i]):list_followers})
            print dict_followers
            f_write.write(cjson.encode(dict_followers)+"\n")
    f_failed.close()
    f_write.close()
    #return user_tweets

def output_user_files(user_profiles, filename):
    out_file = open(filename, 'w')
    for user_profile in user_profiles:
        json.dump(user_profile, out_file)
        out_file.write("\n")
    out_file.close()

def main():
    users = read_user_ids("../user_data/user_withId_list.txt")
    users = users[0:200]
    get_user_followers(users)
    #output_user_files(user_followers, "../user_data/user_followers.json")
    
if __name__ == "__main__":
    main()
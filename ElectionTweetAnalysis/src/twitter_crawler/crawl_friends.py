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

def get_user_friends(users):
    access_twitter_api = ata.Main(APP_CONSUMER_KEY, APP_CONSUMER_SECRET)
    users = users
    f_write = open("../user_data/user_friends.json","w")
    f_failed = open("failed_trails/userList_crawlfriends.txt","w")
    # https://api.twitter.com/1.1/followers/ids.json?cursor=-1&screen_name=sitestreams&count=5000
    URL = "https://api.twitter.com/1.1/friends/ids.json"
    for i in range(len(users)):
        list_friends = []
        dict_friends = {}
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
                    list_friends.extend(content['ids'])
                    print "Crawled user friends with cursor %d: %d" %(cursor, users[i])
                    cursor = content['next_cursor']
            except:
                print "Failed at crawling user friends: %d" %(users[i])
                f_failed.write(str(users[i])+"\n")
                break
        if len(list_friends) != 0:
            dict_friends.update({str(users[i]):list_friends})
            print dict_friends
            f_write.write(cjson.encode(dict_friends)+"\n")
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
    get_user_friends(users)
    #output_user_files(user_friends, "../user_data/user_friends.json") 

if __name__ == "__main__":
    main()
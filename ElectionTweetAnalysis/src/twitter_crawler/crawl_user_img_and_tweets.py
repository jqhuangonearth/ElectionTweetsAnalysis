import json
import os
from twitter_crawler import TwitterCrawler

def read_user_ids(filename):
    in_file = open(filename, 'r')
    lines = in_file.readlines()
    in_file.close()
    user_ids = []
    for line in lines:
        line = line.split()
        user_ids.append(int(line[1].strip()))
    return user_ids

def read_user_ids_from_candidates_info(filename):
    in_file = open(filename, 'r')
    lines = in_file.readlines()
    in_file.close()
    user_ids = []
    for line in lines:
        data = json.loads(line.strip())
        user_ids.append(data['user_id'])
    return user_ids
    
def crawl_user_profiles(tc, user_ids):
    user_profiles = []
    count = 0
    for user_id in user_ids:
        failed_count = 0
        while failed_count < 3:
            try:
                user = tc.crawl_user_profile(user_id = user_id)
                if not user:
                    break
                user_profiles.append(user)
                print "Crawled user:", user_id
                break
            except:
                print "Failed at crawling user:", user_id
                failed_count += 1
        count += 1
        if count % 100 == 0:
            print "Processed %d users." %(count)
    return user_profiles

def crawl_user_tweets(tc, user_ids, number_of_tweets_to_crawl):
    user_tweets = []
    count = 0
    f_failed = open("failed_trails/userList.txt","w")
    for user_id in user_ids:
        failed_count = 0
        while failed_count < 3:
            try:
                tweets = tc.crawl_user_tweets(user_id, number_of_tweets_to_crawl)
                if tweets == []:
                    break
                user_tweets.extend(tweets)
                print "Crawled tweets for user:", user_id
                break
            except Exception as e:
                print str(e)
                print "Failed at crawling user's tweets:", user_id
                failed_count += 1
                if failed_count == 3:
                    f_failed.write(str(user_id)+"\n")
        count += 1
        if count % 20 == 0:
            print "Processed %d users' tweets." %(count)
    f_failed.close()
    return user_tweets

def crawl_user_profile_images(user_profiles, output_directory):
    for user_profile in user_profiles:
        os.system("wget -O %s%d.jpg %s" %(
            output_directory,
            user_profile['id'],
            user_profile['profile_image_url']))

def output_user_profiles(user_profiles, filename):
    out_file = open(filename, 'w')
    for user_profile in user_profiles:
        json.dump(user_profile, out_file)
        out_file.write("\n")
    out_file.close()

def read_user_profiles(filename):
    in_file = open(filename, 'r')
    lines = in_file.readlines()
    in_file.close()
    user_profiles = []
    for line in lines:
        user_profiles.append(json.loads(line.strip()))
    return user_profiles
    
def output_user_tweets(user_tweets, filename):
    out_file = open(filename, 'w')
    for tweet in user_tweets:
        json.dump(tweet, out_file)
        out_file.write("\n")
    out_file.close()

def main():
    tc = TwitterCrawler()
    user_ids = read_user_ids("user_withId_list.txt")
    #user_ids = user_ids[0:100]
    #print user_ids
    user_profiles = crawl_user_profiles(tc, user_ids)
    output_user_profiles(user_profiles, "user_data/sample_user_profiles.json")

    number_of_tweets_to_crawl = 200
    user_tweets = crawl_user_tweets(tc, user_ids, number_of_tweets_to_crawl)
    output_user_tweets(user_tweets, "user_data/sample_user_tweets.json")

    #crawl_user_profile_images(user_profiles, "user_profile_images/")

if __name__ == "__main__":
    main()

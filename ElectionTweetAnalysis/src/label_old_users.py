from pymongo import Connection

def label_oldusers():
    f = open("labelled_users.txt", "r")
    fo = open("users_old.txt", "w")
    conn = Connection('localhost', 27017)
    db = conn['election_analysis']
    #0 - campaigners, 1 - neutral
    for l in f:
        l = l.strip()
        it = db['user_vector'].find({'_id': l})
        #print it
        for j in it:
            if j['class'] == 0:
                fo.write("%s %d %s \n" %(l, j['election_tweet_count'], 'c'))
            else:
                fo.write("%s %d %s\n" %(l, j['election_tweet_count'], 'n'))
                #fo.write("%s %d\n" %(l, j['class']))
            #db['user_vector'].update({'_id': j['_id']}, j, upsert=False)
    f.close()
    fo.close()
        
def main():
    label_oldusers()
    
if __name__ == "__main__":
    main()
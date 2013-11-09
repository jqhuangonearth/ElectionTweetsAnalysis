import random
'''
getnewtarget.py
@author: Bolun Huang
get new users that are not in the dataset
'''

def getnewtarget():
    labelled_users = []
    f1 = open('user_data/labelled_users_new_2.txt', 'r')
    for line in f1:
        line = line.split()
        labelled_users.append(line[0])
    f1.close()
    f2 = open('user_data/high_vol_tweeters', 'r')
    tweeters = []
    cnt = []
    for x in f2.readlines():
        line = x.split()
        tweeters.append(line[0])
        cnt.append(line[1])
        #print line
#    tweeters = [x.split()[0] for x in f2]
    #cnt = [x.split(" ")[1] for x in f2]
 #   cnt = []
#    for x in f2:
 #       val = x.split(" ")[1]
  #      print val
   #     cnt.append(val)
        
    #print tweeters
    #print cnt
    #print tweeters[0:100]
    f2.close()
    length = len(tweeters)
    print "number of high vol tweeters %d" %(length)
    newusers = []
    counts2 = []
    for x in range(0,length-1):
        if not tweeters[x] in labelled_users:
            newusers.append(tweeters[x])
            counts2.append(cnt[x])
            
    #print newusers
    print "number of not lablled tweeters %d" %(len(newusers))
    f3 = open('user_data/not_labelled_users.txt', 'w')
    for x in range(0, len(newusers)):
        f3.write(newusers[x]+' ')
        f3.write(counts2[x]+'\n')
    f3.close()

def to_be_labelled():
    f =  open('user_data/not_labelled_users.txt','r')
    f1 = open('user_data/to_be_labelled_1.txt','w')
    f2 = open('user_data/to_be_labelled_2.txt','w')
    f3 = open('user_data/to_be_labelled_3.txt','w')
    f4 = open('user_data/to_be_labelled_4.txt','w')
    f5 = open('user_data/to_be_labelled_5.txt','w')
    f6 = open('user_data/to_be_labelled_6.txt','w')
    f7 = open('user_data/to_be_labelled_7.txt','w')
    f8 = open('user_data/to_be_labelled_8.txt','w')
    f9 = open('user_data/to_be_labelled_9.txt','w')
    f10 = open('user_data/to_be_labelled_10.txt','w')
    '''f11 = open('user_data/to_be_labelled_11.txt','w')
    f12 = open('user_data/to_be_labelled_12.txt','w')
    f13 = open('user_data/to_be_labelled_13.txt','w')
    f14 = open('user_data/to_be_labelled_14.txt','w')
    f15 = open('user_data/to_be_labelled_15.txt','w')
    f16 = open('user_data/to_be_labelled_16.txt','w')
    f17 = open('user_data/to_be_labelled_17.txt','w')
    f18 = open('user_data/to_be_labelled_18.txt','w')
    f19 = open('user_data/to_be_labelled_19.txt','w')
    f20 = open('user_data/to_be_labelled_20.txt','w')'''
    not_labelled_users = []
    for line in f:
        line = line.split()
        not_labelled_users.append(line)
        #print line,
    for i in range(0, len(not_labelled_users)):
        try:
            if i <= 5000:
                if i%50 == 0:
                    j = int(i+random.random()*50)
                    f1.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f2.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f3.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f4.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f5.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f6.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')                    
                    j = int(i+random.random()*50)
                    f7.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f8.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f9.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*50)
                    f10.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')                    
            else:
                if i%300 == 0:
                    j = int(i+random.random()*300)
                    f1.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f2.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f3.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f4.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f5.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f6.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f7.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f8.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f9.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
                    j = int(i+random.random()*300)
                    f10.write(not_labelled_users[j][0]+' '+not_labelled_users[j][1]+'\n')
        except:
            pass
    f.close()
    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()
    f6.close()
    f7.close()
    f8.close()
    f9.close()
    f10.close()    
    
if __name__ == "__main__":
    #getnewtarget()
    to_be_labelled()



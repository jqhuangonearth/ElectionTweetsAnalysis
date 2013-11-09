from pymongo import Connection

#def find_newusers():
conn = Connection('localhost', 27017)
db = conn['election_analysis']
f1 = open('journalist.txt', 'r')
ids = [x.split()[1] for x in f1]
#print ids
f1.close()
f2 = open('journalist_exist.txt', 'w')
f3 = open('journalist_nonexist.txt', 'w')

for l in ids:
    it = db['user_vector'].find({'_id' : l});
    if it.count()==1: # found
        f2.write(l+'\n')
    if it.count()==0: # found
        f3.write(l+'\n')

f2.close()
f3.close()

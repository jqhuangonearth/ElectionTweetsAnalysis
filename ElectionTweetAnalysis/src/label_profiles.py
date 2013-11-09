from pymongo import Connection

def label_vectors():
	f = open('labelled_users.txt', 'a')
	already_labelled = [x for x in f.readlines()]
	conn = Connection('localhost', 27017)
	count = 0
	db = conn['election_analysis']
	it = db['user_vector'].find()
	for i in it:
		if i['_id'] in already_labelled:
			continue
		for key in i:
			if key == 'tweets':
				print key, ": ["
				for j in i[key]:
					print "\t", j
				print "]"
			else:
				print key, ": ", i[key]
		#0 - campaigners, 1 - neutral
		class_ = raw_input("Class: ")
		if class_ == '0' or class_ == '1':
			i['class'] = int(class_)
			db['user_vector'].update({'_id': i['_id']}, i, upsert=False)
			f.write(i['_id'] + '\n')
			count += 1
			if count > 499:
				return
		else:
			continue
	f.close()

def label_vectors_1():
	conn = Connection('localhost', 27017)
	db = conn['election_analysis']
	fc = open('campaigners.txt', 'r')
	cmps = [x.strip() for x in fc.readlines()]
	cmps.append('DefeatMitts')
	cmps.append('TrinaCuppett')
	cmps.append('ThisisTrixx')
	for i in cmps:
		it = db['user_vector'].find({'_id': i})
		for j in it:
			j['class'] = 0
			db['user_vector'].update({'_id': j['_id']}, j, upsert=False)
			print j
	
	fnc = open('non-campaigners.txt', 'r')
	ncmps = [x.strip() for x in fnc.readlines()]
	ncmps.append('__Politics')
	ncmps.append('Alva_Dias')
	ncmps.append('HeidiL_RN')
	ncmps.append('USRealityCheck')
	ncmps.append('WiseUpLibs')
	for i in ncmps:
		it = db['user_vector'].find({'_id': i})
		for j in it:
			j['class'] = 1
			db['user_vector'].update({'_id': j['_id']}, j, upsert=False)
			print j

def labelled_users():
	conn = Connection('localhost', 27017)
	db = conn['election_analysis']
	f = open('labelled_users.txt', 'w')
	it = db['user_vector'].find({'class': {'$exists': 'true'}})
	for i in it:
		f.write(i['_id']+'\n')
	f.close()

if __name__ == "__main__":
	#label_vectors_1()
	labelled_users()

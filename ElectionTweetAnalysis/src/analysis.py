import cjson
import operator

f = open('../data/results/filter/tweets', 'r')
user_tweet_count_map = {}
for l in f:
	data = cjson.decode(l)
	sn = data['u']['sn']
	if sn in user_tweet_count_map:
		user_tweet_count_map[sn] += 1
	else:
		user_tweet_count_map[sn] = 1
sorted_map = sorted(user_tweet_count_map.iteritems(), key=operator.itemgetter(1), reverse=True)
f.close()
f1 = open('../data/results/filter/high_vol_tweeters', 'w')
for (k, v) in sorted_map:
	if v >= 3:
		f1.write(k+' '+str(v)+'\n')
f1.close()

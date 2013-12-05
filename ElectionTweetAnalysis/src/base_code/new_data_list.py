"""
@description: this program grab a new list of data that would feed into the twitter 
api to grab the most recent tweets that they have as our new dataset 
@author: bolun
"""
import cjson

class script:
    def __init__(self):
        self.user_list = []
        
    def grab(self):
        fr = open("user_data/labelled_new.txt","r")
        for line in fr:
            line = line.split()
            if len(line) == 4:
                try:
                    f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(line[0]), "r")
                    for l in f:
                        data = cjson.decode(l)
                        if "u" in data:
                            if "id" in data["u"]:
                                uid = data["u"]["id"]
                                self.user_list.append([line[0], uid])
                                break
                            else:
                                break
                        else:
                            break
                    f.close()
                except Exception as e:
                    print "%s" %e
                    pass
            else:
                pass
        fr.close()
        fr = open("user_data/to_be_labelled_8.txt","r")
        for line in fr:
            line = line.split()
            try:
                f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(line[0]), "r")
                for l in f:
                    data = cjson.decode(l)
                    if "u" in data:
                        if "id" in data["u"]:
                            uid = data["u"]["id"]
                            self.user_list.append([line[0], uid])
                            break
                        else:
                            break
                    else:
                        break
            except Exception as e:
                print "%s" %e
                pass
        fr.close()
        fr = open("user_data/to_be_labelled_9.txt","r")
        for line in fr:
            line = line.split()
            try:
                f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(line[0]), "r")
                for l in f:
                    data = cjson.decode(l)
                    if "u" in data:
                        if "id" in data["u"]:
                            uid = data["u"]["id"]
                            self.user_list.append([line[0], uid])
                            break
                        else:
                            break
                    else:
                        break
            except Exception as e:
                print "%s" %e
                pass
        fr.close()
        fr = open("user_data/to_be_labelled_10.txt","r")
        for line in fr:
            line = line.split()
            try:
                f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(line[0]), "r")
                for l in f:
                    data = cjson.decode(l)
                    if "u" in data:
                        if "id" in data["u"]:
                            uid = data["u"]["id"]
                            self.user_list.append([line[0], uid])
                            break
                        else:
                            break
                    else:
                        break
            except Exception as e:
                print "%s" %e
                pass
        fr.close()
        print self.user_list
        print len(self.user_list)
        user_dic = {}
        for i in range(len(self.user_list)):
            if self.user_list[i][0] not in user_dic:
                user_dic.update({self.user_list[i][0] : self.user_list[i][1]})
        print len(user_dic)
        fw = open("user_data/user_withId_list.txt","w")
        for u in user_dic:
            fw.write("%s %d\n" %(u, user_dic[u]))
        fw.close()

def main():
    myscript = script()
    myscript.grab()


if __name__ == "__main__":
    main()
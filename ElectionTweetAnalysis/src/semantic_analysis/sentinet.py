"""
This script analyzes the sentinet dataset so as to test it and probably use it
as a tool to analyze the sentiment score of tweets
@author: Bolun Huang
"""
import json

class sentinet:
    def __init__(self):
        self.sentiwords = {}
        
    def get_sentiwords(self, filename):
        f = open(filename, "r")
        count = 0
        for line in f:
            count += 1
            if not line.startswith("#"):
                data = line.split("\t")
                try:
                    if not float(data[2]) == 0 and not float(data[3]) == 0:
                        score = float(data[2]) - float(data[3])
                        words = data[4].split()
                        for word in words:
                            w_01 = word.split("#")
                            if not self.sentiwords.has_key(w_01[0]):
                                self.sentiwords.update({w_01[0] : {w_01[1] : score}})
                            else:
                                self.sentiwords[w_01[0]].update({w_01[1] : score})
                except:
                    pass

        f.close()
        print len(self.sentiwords)
        
        for word in self.sentiwords:
            summation = 0.0
            count = 0
            for score in self.sentiwords[word]:
                summation += self.sentiwords[word][score]
                count += 1
            score = summation/float(count)
            self.sentiwords[word] = score
            
        f = open("SentiWordNet/data/SentiWord.json","w")
        json.dump(self.sentiwords, f)
        f.close()

        
def main():
    st = sentinet()
    st.get_sentiwords("SentiWordNet/data/SentiWordNet_3.0.0_20130122.txt")
    
if __name__ == "__main__":
    main()
        
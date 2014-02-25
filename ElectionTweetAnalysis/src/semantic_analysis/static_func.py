import re
import nltk

class static_fucntions:
    @staticmethod
    def process_sentence(text):
        """
        process the sentence and return a list of lower case words/terms
        remove stopwords; remove url, '\'w'.
        """
        text1 = ""
        try:
            # to lower case
            text1 = text.lower()
            # remove url
            text1 = re.sub(r'http:[\\/.a-z0-9]+\s?', '', text1)
            text1 = re.sub(r'https:[\\/.a-z0-9]+\s?', '', text1)
            # rmove mentioned user names
            text1 = re.sub(r'(@\w+\s?)|(@\s+)', '', text1) 
            # remove special characters
            text1 = re.sub(r'[\#\-\+\*\`\.\;\:\"\<\>\[\]\{\}\|\~\_\=\^\&\(\)]', '', text1) 
            # remove retweet tag
            #text1 = re.sub(r'rt\s?', '', text1)
        except:
            print text1
            pass
        try:
            text1 = nltk.word_tokenize(text1)
        except:
            text1 = []
            pass
        words = []
        for i in range(len(text1)):
            if "'" in text1[i] or text1[i] in nltk.corpus.stopwords.words('english'):
                pass
            else:
                words.append(text1[i])
        return words
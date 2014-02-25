"""
read from the user_profiles_shortened.txt
and find the profile of labelled users
"""
import cjson

class contruct_profile:
    def __init__(self):
        self.profile_vector = {}
        self.user_list = []
    
    """ read the user list from data/labelled_user_new.txt """
    def read_user_list(self):
        f = open("data/labelled_user_new.txt", "r")
        for line in f:
            if not line.startswith("#"):
                line = line.split()
                self.user_list.append(line[0].strip())
        f.close()
    
    def read_user_profile(self):
        f = open("../user_profiles_shortened.txt","r")
        fw = open("user_vector/user_profile.json","w")
        for line in f:
            data = cjson.decode(line)
            if data["screen_name"] in self.user_list:
                fw.write(cjson.encode(data)+"\n")
        f.close()
        fw.close()
    
    
    
    
def main():
    c = contruct_profile()
    c.read_user_list()
    c.read_user_profile()
    
if __name__ == "__main__":
    main()
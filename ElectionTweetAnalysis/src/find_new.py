def find_new_user():
    f = open("not_labelled_users.txt", "r")
    fo = open("users_new.txt","w")
    c = 0
    n = 0
    for l in f:
        l.strip()
        l = l.split()
        if len(l)==3:
            if l[2] == 'c':
                fo.write(l[0]+" "+l[1]+" "+l[2]+"\n")
                c = c + 1
            elif l[2] == 'n':
                fo.write(l[0]+" "+l[1]+" "+l[2]+"\n")
                n = n + 1
    fo.write("c: %d n: %d" %(c, n))
    f.close()
    fo.close()
    
def main():
    find_new_user()
    
if __name__ == '__main__':
    main()
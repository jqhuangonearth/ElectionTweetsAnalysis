'''
@author: Bolun Huang
@summary: find retweet graph
'''
from pymongo import Connection
import matplotlib.pyplot as plt
import networkx as nx
import cjson

class RT_graph:
    def __init__(self):
        self.conn = Connection('localhost', 27017)
        self.db = self.conn['election_analysis']
        self.f = open("data/labelled_users_new.txt","r")
        self.G = nx.DiGraph() # internal graph
        self.extr_G = nx.DiGraph() # external graph
        self.whole_G = nx.DiGraph() # complete graph
        self.neutral = []
        self.campaigner = []
        self.retweet = []
        self.dic_users = {}
        self.extr_dic_users = {}
        
    def find_RT_graph(self):
        for l in self.f:
            l = l.split()
            self.G.add_node(l[0], type = l[1])
            self.extr_G.add_node(l[0], type = l[1])
            # { username : [ tweet_count, type]}
            self.dic_users.update({l[0] : [l[1], l[2]]})
            if l[2] == 'c':
                self.campaigner.append(l[0])
            else:
                self.neutral.append(l[0])
        self.f.close()
        print self.dic_users
        for user in self.dic_users:
            rt_percent = 0
            rt_num_same = 0 # to keep track of how many rts are from the same group
            rt_total = 0 # total number of retweet in this dataset
            it = self.db['user_vector'].find({'_id': user})
            for j in it:
                tweet = j['tweets']
                #print tweet
                for i in tweet:
                    tmp = i
                    if tmp.startswith("RT @"):
                        tmp = tmp.split("RT @")
                        tmp2 = tmp[1].split(" ")
                        sn = tmp2[0].strip(":") # rt_from name
                        if sn in self.dic_users:
                            rt_total = rt_total + 1
                            self.G.add_edge(user, sn, weight = 1)
                            # if they are in the same group and have direct RT relation
                            if self.dic_users[sn][1] == self.dic_users[user][1]:
                                rt_num_same = rt_num_same + 1
                        else:
                            # add these people in the dictionary as undefined type of "nc"
                            self.extr_dic_users.update({sn : [0, 'nc']})
                if not rt_total == 0:
                    rt_percent = rt_num_same/float(rt_total)
                    print rt_percent
                else:
                    rt_percent = 0.01 # if they have no retweets, set this metric to 0.01
            self.dic_users[user].append(rt_percent)
            # the dictionary becomes { user : [ num_tweet, type, rt_percent]}
        print "len of users: %d\n" %(len(self.dic_users))
        print self.dic_users
        self.whole_G = self.G.copy()
        count = 0
        for user in self.extr_dic_users:
            self.retweet.append(user)
            self.extr_G.add_node(user)
            self.whole_G.add_node(user)
        print "len of retweet: %d\n" %(len(self.retweet))

        
    def analysis_Graph(self):
        '''
        @summary: extract metrics in the rt_graph, including out_degree, in_degree
        '''
        c = 0
        for user in self.campaigner:
            if not self.G.degree(user, weight = 'weight') == 0:
                o_degree = self.G.out_degree(user, weight = 'weight')
                i_degree = self.G.in_degree(user, weight = 'weight')
                print '{} '.format(user).ljust(20)+'{} '.format(str(o_degree)).ljust(5)+'%d' %(i_degree)
        print "campaigners with no RT:\n"
        for user in self.campaigner:
            if self.G.degree(user, weight = 'weight') == 0:
                print user
                c = c + 1
        print 'campaigner with 0 rt: %d' %(c)
        c = 0
        for user in self.neutral:
            if not self.G.degree(user, weight = 'weight') == 0:
                o_degree = self.G.out_degree(user, weight = 'weight')
                i_degree = self.G.in_degree(user, weight = 'weight')
                print '{} '.format(user).ljust(20)+'{} '.format(str(o_degree)).ljust(5)+'%d' %(i_degree)
        print "neutral users with no RT:"
        for user in self.neutral:
            if self.G.degree(user, weight = 'weight') == 0:
                print user
                c = c + 1
        print 'neutral with 0 rt: %d' %(c)
        for user in self.dic_users:
            it = self.db['user_vector'].find({'_id': user})
            for j in it:
                tweet = j['tweets']
                #print tweet
                for i in tweet:
                    tmp = i
                    if tmp.startswith("RT @"):
                        tmp = tmp.split("RT @")
                        tmp2 = tmp[1].split(" ")
                        sn = tmp2[0].strip(":") # rt_from name
                        if sn in self.retweet:
                            self.extr_G.add_edge(user, sn, weight = 1)
                            self.whole_G.add_edge(user, sn, weight = 1)

    def draw_graph(self):
        val_map = {}
        for user in self.dic_users:
            if self.dic_users[user][1] == 'c':
                val_map.update({ user : 'r'})
            else:
                val_map.update({ user : 'b'})
        #for user in self.extr_dic_users:
        #    val_map.update({ user : 'g'})
        #self.G = self.G.to_undirected()
        values = [val_map.get(node) for node in self.G.nodes()]
        nx.draw(self.G, pos = nx.random_layout(self.G, dim = 2), randomcmap = plt.get_cmap('jet'), node_color = values, width = 1, node_size = 200, with_labels=True)
        #nx.draw_networkx(self.G, pos=nx.random_layout(self.G), with_labels=True)
        #nx.convert_node_labels_to_integers(G)
        #nx.draw_networkx_nodes(self.G, pos=nx.random_layout(self.G), nodelist = self.campaigner, node_color = 'r', label = None)
        #nx.draw_networkx_edges(self.G, pos=nx.random_layout(self.G))
        plt.show()
    # type = "internal", "external" or "whole"
    def output_files(self, typ):
        f1 = open("data/rt_graph_%s.txt" %(typ), "w")
        f1.write("nodes\n")
        if typ == 'internal':
            for node in self.G.nodes(data = True):
                f1.write("%s %d %d\n" %(node[0], self.whole_G.out_degree(node[0], weight = 'weight'), self.whole_G.in_degree(node[0], weight = 'weight')))
                self.dic_users[node[0]].append(self.whole_G.out_degree(node[0], weight = 'weight'))
                self.dic_users[node[0]].append(self.whole_G.in_degree(node[0], weight = 'weight'))
                # dic_users becomes : { user : [num_tweet, type, rt_percent, out_degree, in_degree]}
        elif typ == 'external':
            for node in self.extr_G.nodes(data = True):
                f1.write("%s %d %d\n" %(node[0], self.extr_G.out_degree(node[0], weight = 'weight'), self.extr_G.in_degree(node[0], weight = 'weight')))
        elif typ == 'whole':
            for node in self.whole_G.nodes(data = True):
                f1.write("%s %d %d\n" %(node[0], self.whole_G.out_degree(node[0], weight = 'weight'), self.whole_G.in_degree(node[0], weight = 'weight')))
        f1.write("edges\n")
        if typ == 'internal':
            for edge in self.G.edges():
                f1.write("%s %s\n" %(edge[0], edge[1]))
        elif typ == 'external':
            for edge in self.extr_G.edges():
                f1.write("%s %s\n" %(edge[0], edge[1]))
        elif typ == 'whole':
            for edge in self.whole_G.edges():
                f1.write("%s %s\n" %(edge[0], edge[1]))
        f1.close()
        f1 = open("rt_graph_metrics.txt","w")
        f1.write('{} '.format("user_name").ljust(20)+'{} '.format("num_twts").ljust(10)+'{} '.format("user_type").ljust(10)+'{} '.format("out_deg").ljust(10)+'in_deg\n')
        for user in self.dic_users:
            f1.write('{} '.format('%s' %(user)).ljust(20)+'{} '.format("%s" %(str(self.dic_users[user][0]))).ljust(10)+'{} '.format("%s" %(self.dic_users[user][1])).ljust(10)+'{} '.format("%s" %(str(self.dic_users[user][3]))).ljust(10)+'%s\n' %(str(self.dic_users[user][4])))
        f1.close()
        
def main():
    rt = RT_graph()
    rt.find_RT_graph()
    rt.analysis_Graph()
    rt.output_files('internal')
    rt.draw_graph()
    
if __name__ == "__main__":
    main()
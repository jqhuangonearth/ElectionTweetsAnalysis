'''
@author: Bolun Huang
@summary: generate the user mention graph
extract metrices like: average user mentions; mention graph degree for each node
'''
'''
@author: Bolun Huang
@summary: find retweet graph
'''
from pymongo import Connection
import matplotlib.pyplot as plt
import networkx as nx
import cjson

class mention_graph:
    def __init__(self):
        self.m_G = nx.DiGraph()
        self.m_extr_G = nx.DiGraph()
        self.neutral = []
        self.campaigner = []
        self.dic_users = {}
        self.dic_high_vol_users = {}
        self.extr_dic_users = {}
        self.f = open("user_data/labelled_new.txt","r")
        self.f2 = open("high_vol_tweeters","r")
        
    def find_mention_graph(self):
        for l in self.f:
            l = l.split()
            self.m_G.add_node(l[0], weight = 1, type = l[1])
            self.dic_users.update({l[0] : [l[1], l[2]]})
            self.extr_dic_users.update({l[0] : l[2]})
            if l[2] == 'c':
                self.campaigner.append(l[0])
            else:
                self.neutral.append(l[0])
        self.f.close()
        self.m_extr_G = self.m_G.copy()
        for l in self.f2:
            l = l.split()
            self.dic_high_vol_users.update({l[0]:0})
        self.f2.close()
        
        count = 0
        for user in self.dic_users:
            f = open("/home/bolun/hbl/ElectionTweetsAnalysis/data/results/user_tweets_new/%s.json" %(user), "r")
            for line in f: # each tweet
                data = cjson.decode(line)
                if 'tx' in data:
                    tx = data['tx']
                if ':x' in data:
                    tx = data[':x']
                tx = tx.split()
                for i in tx:
                    if i.startswith("@"):
                        ii = i.strip('@')
                        ii = ii.strip(':')
                        #################################
                        if ii in self.dic_users:
                            #self.dic_high_vol_users[ii] = 1
                            self.m_G.add_edge(user, ii)
                            self.m_extr_G.add_edge(user, ii)
                        ##### outside the 233 
                        if ii in self.dic_high_vol_users and not ii in self.dic_users:
                            self.extr_dic_users.update({ii : 'nc'})
                            self.m_extr_G.add_node(ii, weight = 1, type = 'nc')
                            self.m_extr_G.add_edge(user, ii)
            f.close()

        
    def analysis_graph(self):
        '''
        @summary: extract metrics in the mention_graph, including out_degree, in_degree
        '''
    #def draw_graph(self):
        
    #def output_files(self, typ):
    def draw_graph(self, type):
        val_map = {}
        if type == 'whole':
            for user in self.extr_dic_users:
                if self.extr_dic_users[user] == 'c':
                    val_map.update({ user : 'r'})
                elif self.extr_dic_users[user] == 'n':
                    val_map.update({ user : 'b'})
                else:
                    val_map.update({ user : 'g'})
            #for user in self.extr_dic_users:
            #    val_map.update({ user : 'g'})
            self.m_extr_G = self.m_extr_G.to_undirected()
            values = [val_map.get(node) for node in self.m_extr_G.nodes()]
            nx.draw(self.m_extr_G, pos = nx.random_layout(self.m_extr_G, dim = 2), randomcmap = plt.get_cmap('jet'), node_color = values, width = 1, node_size = 40, with_labels=False)
            plt.show()
        elif type == 'internal':
            for user in self.dic_users:
                if self.dic_users[user][1] == 'c':
                    val_map.update({ user : 'r'})
                else:
                    val_map.update({ user : 'b'})
            #for user in self.extr_dic_users:
            #    val_map.update({ user : 'g'})
            #self.G = self.G.to_undirected()
            values = [val_map.get(node) for node in self.m_G.nodes()]
            nx.draw(self.m_G, pos = nx.spring_layout(self.m_G, dim = 2), randomcmap = plt.get_cmap('jet'), node_color = values, width = 1, node_size = 200, with_labels=True)
            plt.show()
    
    def analysis(self):
        sum_c_o_i = 0
        sum_c_i_i = 0
        sum_n_o_i = 0
        sum_n_i_i = 0
        sum_c_o = 0
        sum_c_i = 0
        sum_n_o = 0
        sum_n_i = 0
        count_c = 0
        count_n = 0
        f = open("mention.txt", "w")
        f.write('{} '.format("user").ljust(20)+'{} '.format("out_deg_i").ljust(10)+'{} '.format("in_deg_i").ljust(10)+'{} '.format("out+deg").ljust(10)+'{} '.format("in_deg").ljust(10)+'\n')
        for user in self.dic_users:
            o_degree_i = self.m_G.out_degree(user, weight = 'weight')
            i_degree_i = self.m_G.in_degree(user, weight = 'weight')
            o_degree = self.m_extr_G.out_degree(user, weight = 'weight')
            i_degree = self.m_extr_G.in_degree(user, weight = 'weight')
            if self.dic_users[user][1] == 'c':
                count_c = count_c + 1
                sum_c_o_i = sum_c_o_i + o_degree_i
                sum_c_i_i = sum_c_i_i + i_degree_i
                sum_c_o = sum_c_o + o_degree
                sum_c_i = sum_c_i + i_degree
            if self.dic_users[user][1] == 'n':
                count_n = count_n + 1
                sum_n_o_i = sum_n_o_i + o_degree_i
                sum_n_i_i = sum_n_i_i + i_degree_i
                sum_n_o = sum_n_o + o_degree
                sum_n_i = sum_n_i + i_degree
            ### calculate the avg of c an n ###
            f.write('{} '.format(user).ljust(20)+'{} '.format(str(o_degree_i)).ljust(10)+'{} '.format(str(i_degree_i)).ljust(10)+'{} '.format(str(o_degree)).ljust(10)+'{}'.format(str(i_degree)).ljust(10)+'\n')
        agv_c_o_i = sum_c_o_i/float(count_c)### avg of out_deg of campaigner internally
        agv_c_i_i = sum_c_i_i/float(count_c)### avg of in_deg of campaigner internally
        agv_n_o_i = sum_n_o_i/float(count_n)### avg of out_deg of normaluser internally
        agv_n_i_i = sum_n_i_i/float(count_n)### avg of in_deg of normaluser internally
        agv_c_o = sum_c_o/float(count_c)### avg of out_deg of campaigner
        agv_c_i = sum_c_i/float(count_c)### avg of in_deg of campaigner
        agv_n_o = sum_n_o/float(count_n)### avg of out_deg of normaluser
        agv_n_i = sum_n_i/float(count_n)### avg of in_deg of normaluser
        f.write("Internal Mention Graph:\n")
        f.write("avg of out_deg of campaigner: %f\n" %(agv_c_o_i))
        f.write("avg of in_deg of  campaigner: %f\n" %(agv_c_i_i))
        f.write("avg of out_deg of normal user: %f\n" %(agv_n_o_i))
        f.write("avg of in_deg of normal user: %f\n" %(agv_n_i_i))
        f.write("Overall Mention Graph:\n")
        f.write("avg of out_deg of campaigner: %f\n" %(agv_c_o))
        f.write("avg of in_deg of campaigner: %f\n" %(agv_c_i))
        f.write("avg of out_deg of normal user: %f\n" %(agv_n_o))
        f.write("avg of in_deg of normal user: %f\n" %(agv_n_i))
        f.close()   
def main():
    mn = mention_graph()
    mn.find_mention_graph()
    mn.analysis()
    mn.draw_graph('whole')
    
if __name__ == "__main__":
    main()
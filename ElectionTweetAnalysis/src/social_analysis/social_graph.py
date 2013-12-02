"""
build the social graph of our dataset
@author: Bolun Huang
"""
import cjson
import networkx as nx
import matplotlib.pyplot as plt
import json
from pylab import rcParams
import math

class social:
    def __init__(self):
        self.user_dic = {}
        self.user_list = []
        self.user_friends = {}
        self.uid_list = []
        self.G = nx.DiGraph()
        
    def get_user_list(self, filename):
        user_list = []
        f = open(filename, "r")
        for line in f:
            if not line.startswith("#"):
                line = line.split()
                user_list.append([line[0], line[1]])
        f.close()
        return user_list
    
    def read_user_dic(self, filename):
        user_dic = {}
        f = open(filename, "r")
        count = 0
        for line in f:
            data = cjson.decode(line)
            user_dic.update({data["screen_name"] : {"id" : data["id"], "statuses_count" : data["statuses_count"]}}) # add default _id
            count += 1
        f.close()
        return user_dic
        
    def read_user_friends(self, filename):
        user_friends = {}
        f = open(filename, "r")
        for line in f:
            data = cjson.decode(line)
            user_friends.update(data)
        f.close()
        return user_friends

    def construct_user_graph(self):
        self.user_dic = self.read_user_dic("../semantic_analysis/user_vector/user_vector.json")
        self.user_friends = self.read_user_friends("../twitter_crawler/social_graph/user_friends.json")
        self.user_followers = self.read_user_friends("../twitter_crawler/social_graph/user_followers.json")
        
        f = open("../semantic_analysis/data/labelled_id_name_map_393.json", "r")
        id_label_map = cjson.decode(f.readline())
        f.close()
        
        print len(self.user_dic)
        
        all_edges = set() # all crawled edges
        for user in self.user_friends:
            if self.user_dic.has_key(user):
                for friend in self.user_friends[user]:
                    all_edges.add((str(self.user_dic[user]["id"]), str(friend)))
        for user in self.user_followers:
            if self.user_dic.has_key(user):
                for follower in self.user_followers[user]:
                    all_edges.add((str(follower), str(self.user_dic[user]["id"])))
        
        print len(all_edges)
        all_edges_list = list(all_edges)
        remaining_edges = []
        
        for edge1 in all_edges_list:
            if id_label_map.has_key(edge1[0]) and id_label_map.has_key(edge1[1]):
                remaining_edges.append(edge1)
        print len(remaining_edges)
        
        f = open("user_graph/user_graph_393_2.txt","w")
        # write user nodes
        f.write("#nodes\n")
        for id in id_label_map:
            f.write(id+" "+id_label_map[id]["label"]+"\n") # id + status_count
        
        f.write("#edges\n")
        for edge in remaining_edges:
            f.write(edge[0]+" "+edge[1]+"\n")
        f.close()
        
    def construct_graph(self, node_list, edge_list):
        """
        @type node_list: list
        @param node_list: list of uid of users
        
        @type edge_list: list of two tuple list
        @param edge_list: list of edges represented by [uid1, uid2]
        """
        for node in node_list:
            self.G.add_node(node)
        for edge in edge_list:
            self.G.add_edge(edge[0], edge[1])

    def draw_graph(self):
        """
        draw graph
        """
        nx.draw(self.G, pos = nx.random_layout(self.G, dim = 2), randomcmap = plt.get_cmap('jet'), node_color = "blue", alpha = 0.5, width = 1, node_size = 200, with_labels=False)
        plt.show()

    def read_node_edge_lists(self, filename):
        fg = open(filename, "r")
        flag = 0
        node_list = []
        edge_list = []
        for line in fg:
            if flag == 1:
                try:
                    node = line.split(" ")
                    node_list.append([node[0], node[1].rstrip()])
                except:
                    pass
            elif flag == 2:
                try:
                    edge = line.split(" ")
                    edge_list.append([str(int(edge[0].rstrip())), str(int(edge[1].rstrip()))])
                except:
                    pass
            if line.startswith("#nodes"):
                flag = 1
            elif line.startswith("#edges"):
                flag = 2
        fg.close()
        #print len(node_list), len(edge_list)
        #print node_list
        return node_list, edge_list
    
    
    def read_node_edge_lists_screen_name(self, filename):
        fg = open(filename, "r")
        flag = 0
        node_list = []
        edge_list = []
        for line in fg:
            if flag == 1:
                try:
                    node = line.split(" ")
                    node_list.append([node[0], node[1].rstrip()])
                except:
                    pass
            elif flag == 2:
                try:
                    edge = line.split(" ")
                    edge_list.append([edge[0].rstrip(), edge[1].rstrip()])
                except:
                    pass
            if line.startswith("#nodes"):
                flag = 1
            elif line.startswith("#edges"):
                flag = 2
        fg.close()
        #print len(node_list), len(edge_list)
        #print node_list
        return node_list, edge_list
    
    
    
    def transform_graph(self):
        """
        This function transform ids to corresponding screen_name in the user_graph.txt file 
        """
        f = open("../semantic_analysis/data/labelled_user_dic_393.json", "r")
        user_dic = cjson.decode(f.readline())
        f.close()
        
        f = open("../semantic_analysis/data/labelled_id_name_map_393.json", "r")
        id_label_map = cjson.decode(f.readline())
        f.close()
        
        node_list, edge_list = self.read_node_edge_lists("user_graph/user_graph_393_2.txt")
        
        f = open("user_graph/user_graph_393_screen_name_2.txt","w")
        f.write("#nodes-screen_name\n")
        for user in user_dic:
            f.write(user+" "+user_dic[user]["label"]+"\n")
        f.write("#edges-screen_name\n")    
        for edge in edge_list:
            edge_with_name = []
            flag = 0
            for node in edge:
                if id_label_map.has_key(node):
                    edge_with_name.append(id_label_map[node]["screen_name"])
                else:
                    flag = 1
                    break
            if flag == 0:
                f.write(edge_with_name[0]+" "+edge_with_name[1]+"\n")
        f.close()
        
    
    def draw_social_graph(self):
        """
        draw social graph using networkx
        """
        node_list, edge_list = self.read_node_edge_lists("user_graph/user_graph_393.txt")
        self.construct_graph(node_list, edge_list)
        self.draw_graph() # call draw graph
        

    def draw_2_level_social_graph(self, screen_name):
        """
        generate the two level social graph given a screen_name
        @type screen_name: string
        @param screen_name: screen name of a given user
        """
        node_list, edge_list = self.read_node_edge_lists("user_graph/user_graph_393.txt")
        user_dic = {}
        
        f = open("../semantic_analysis/data/labelled_user_dic_393.json", "r")
        user_dic = cjson.decode(f.readline())
        f.close()
        
        f = open("../semantic_analysis/data/labelled_id_name_map_393.json", "r")
        id_label_map = cjson.decode(f.readline())
        f.close()
            
        uid = str(user_dic[screen_name]["id"])
        new_edge = []
        new_node = set()
        for edge in edge_list:
            if uid == edge[1]:
                #new_edge.append(edge)
                new_node.add(edge[0])

        new_node_2 = set()
        for node in new_node:
            for edge in edge_list:
                if node == edge[1]:
                    #new_edge.append(edge)
                    new_node_2.add(edge[0])

        new_node.add(uid)
        new_node_list = list(new_node.union(new_node_2))
        
        for edge in edge_list:
            if edge[0] in new_node_list and edge[1] in new_node_list:
                new_edge.append(edge)
        
        new_node_color = []
        for node in new_node_list:
            if id_label_map[node]["label"] == "d":
                new_node_color.append("b")
            elif id_label_map[node]["label"] == "r":
                new_node_color.append("r")
        
        new_node_size = []
        maxi = 0
        for user in user_dic:
            if user_dic[user]["statuses_count"] > maxi:
                maxi = user_dic[user]["statuses_count"]
            else:
                pass
        
        for node in new_node_list:
            new_node_size.append(math.log(id_label_map[node]["statuses_count"]/float(maxi)+1)*5000.0)
        print self.G.nodes()
        self.construct_graph(new_node_list, new_edge)
        print self.G.nodes()
        rcParams['figure.figsize'] = 20, 16
        nx.draw(self.G, pos = nx.random_layout(self.G, dim = 2), randomcmap = plt.get_cmap('jet'), font_size = 20, node_color = new_node_color, alpha = 0.5, width = 0.5, node_size = new_node_size, with_labels=False)
        plt.savefig("figures/%s_%s.png" %(screen_name, id_label_map[uid]["label"]), dpi = 100)
        #plt.show()
        plt.clf()
        self.G.clear()
        
    def draw_2_level_social_graph_screen_name(self, screen_name):
        """
        generate the two level social graph given a screen_name
        @type screen_name: string
        @param screen_name: screen name of a given user
        """
        node_list, edge_list = self.read_node_edge_lists_screen_name("user_graph/user_graph_393_screen_name.txt")
        user_dic = {}
        
        f = open("../semantic_analysis/data/labelled_user_dic_393.json", "r")
        user_dic = cjson.decode(f.readline())
        f.close()
        
        new_edge = []
        new_node = set()
        for edge in edge_list:
            if screen_name == edge[1]:
                #new_edge.append(edge)
                new_node.add(edge[0])

        new_node_2 = set()
        for node in new_node:
            for edge in edge_list:
                if node == edge[1]:
                    #new_edge.append(edge)
                    new_node_2.add(edge[0])

        new_node.add(screen_name)
        
        new_node_list = list(new_node.union(new_node_2))
        
        for edge in edge_list:
            if edge[0] in new_node_list and edge[1] in new_node_list:
                new_edge.append(edge)
        
        new_node_color = []
        for node in new_node_list:
            if user_dic[node]["label"] == "d":
                new_node_color.append("b")
            elif user_dic[node]["label"] == "r":
                new_node_color.append("r")

        self.construct_graph(new_node_list, new_edge)
        
        new_node_size = []
        for node in new_node_list:
            indegree = self.G.in_degree(node)
            if node == screen_name:
                new_node_size.append(indegree*20+5000)
            else:
                new_node_size.append(indegree*20+1000)
        
        rcParams['figure.figsize'] = 20, 16
        nx.draw(self.G, pos = nx.random_layout(self.G, dim = 2), randomcmap = plt.get_cmap('jet'), node_color = new_node_color, alpha = 0.5, width = 0.5, node_size = new_node_size, with_labels=True)
        plt.savefig("figures/%s_%s_labelled.png" %(screen_name, user_dic[screen_name]["label"]), dpi = 100)
        #plt.show()
        plt.clf()
        self.G.clear()
        
    
def main():
    sg = social()
    sg.construct_user_graph()
    #sg.draw_social_graph()
    #sg.draw_2_level_social_graph("MsNatTurner")
    #sg.draw_2_level_social_graph("WashingtonDCTea")
    #sg.draw_2_level_social_graph_screen_name("MsNatTurner")
    #sg.draw_2_level_social_graph_screen_name("IBumbybee")
    #sg.transform_graph()
    
if __name__ == "__main__":
    main()
    
        
    
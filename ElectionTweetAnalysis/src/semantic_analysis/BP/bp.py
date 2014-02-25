"""
@author: Bolun
@description: use belief propagation to classify in a graph
"""
import networkx as nx
import matplotlib.pyplot as plt
import random
import time
from sklearn import metrics
import numpy as np

def beliefprop(graph, _base_message_set={}, nodes_belief = {}, max_iterations=100, min_delta=0.0001):
    """
    @description: implementation of belief propagation referencing sandeep's thesis paper
    
    @param graph: graph
    @type graph: networkx DiGraph
    
    @param base_message_set: initial messages of the graph
    @type base_message_set: dict
    
    @param nodes_belief: node belief
    @type nodes_belief: dict
    
    @param max_iterations: maximum number of iters
    @type max_iterations: int
    
    @param min_delta: convergence mininum delta
    @type min_delta: float
    
    @return: new_node_belief (a dict)
    @return: stable message scores (a dict) 
    """
    base_message_set = _base_message_set
    i = 0
    for i in range(max_iterations):
        old_base_message_set = dict()
        old_base_message_set.update({key : base_message_set[key] for key in base_message_set.keys()})
        
        for message in old_base_message_set.keys():
            new_msg = []
            sigma = 0.0
            # update "b" msg
            neighbors = graph.in_edges(message.split('#')[0])
            #print "before ", base_message_set[message]
            for j in range(2): ## j from b to r
                product = 1.0
                #print sigma, neighbors
                if len(neighbors) == 0:
                    sigma = 1.0
                else:
                    for node in neighbors:
                        if node[0] != message.split("#")[1]:
                            product *= 1.0*old_base_message_set[node[0]+"#"+node[1]][j]
                    if j == 0:
                        sigma += (1.0*nodes_belief[message.split("#")[0]][0]*0.85*product)
                    else:
                        sigma += (1.0*nodes_belief[message.split("#")[0]][1]*0.15*product)
            #print sigma,
            new_msg.append(sigma)
            sigma = 0.0
            # update "r" msg
            for j in range(2): ## j from b to r
                product = 1.0
                #print sigma, neighbors
                if len(neighbors) == 0:
                    sigma = 1.0
                else:
                    for node in neighbors:
                        if node[0] != message.split("#")[1]:
                            product *= 1.0*old_base_message_set[node[0]+"#"+node[1]][j]
                    if j == 0:
                        sigma += (1.0*nodes_belief[message.split("#")[0]][0]*0.15*product)
                    else:
                        sigma += (1.0*nodes_belief[message.split("#")[0]][1]*0.85*product)
            #print sigma
            new_msg.append(sigma)
            base_message_set[message] = new_msg
            #print "after ", base_message_set[message]
        
        base_message_set = normalize(base_message_set) # normalization
        delta = sum((abs(base_message_set[k][0] - old_base_message_set[k][0]) for k in base_message_set))
        if delta < min_delta:
            break
            #return base_message_set
    print "bp_iter: ",i, " ",
    """compute the new belief"""
    new_nodes_belief = {}
    b_b = 0.0
    b_r = 0.0
    for node in nodes_belief:
        neighbors = graph.in_edges(node)
        product = 1.0
        for n in neighbors:
            product *= base_message_set[n[0]+"#"+node][0]
        b_b = nodes_belief[node][0]*product
        product = 1.0
        for n in neighbors:
            product *= base_message_set[n[0]+"#"+node][1]
        b_r = nodes_belief[node][1]*product
        new_nodes_belief.update({node : [b_b, b_r]})
    new_nodes_belief = normalize(new_nodes_belief)
    return new_nodes_belief, base_message_set
        
def normalize(_adict):
    """
    @description: normalization
    
    @param _adict: input dict
    @type _adict: dict
    
    @return: normalized dict
    """
    ndict = {}
    for key in _adict:
        norm_list = []
        total = sum(_adict[key])
        norm_list = [a / float(total) for a in _adict[key]]
        ndict[key] = norm_list
    return ndict
    

def read_node_edge_lists(filename):
    """
    @description: helper function to read node_list and edge_list from a file
    
    @param filename: path and name of file
    @type filename: string
    
    @return: node_list - list of nodes [node_name, node_label]
    @return: edge_list - list of edges [src_node, dst_node]
    """
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
    return node_list, edge_list

class bp:
    def __init__(self):
        self.G = nx.DiGraph()
        self.node_list = []
        self.nodes_label = {}
        
    def read_graph(self, filename):
        self.node_list, edge_list = read_node_edge_lists(filename)
        for node in self.node_list:
            self.G.add_node(node[0])
        for edge in edge_list:
            self.G.add_edge(edge[0], edge[1])
        for node in self.node_list:
            self.nodes_label.update({node[0] : node[1]})
    
    def evaluation(self, node_label = {}, node_belief = {}, root_set = []):
        """
        @param node_label: dict of node belief
        @type node_label: dict
        
        @param node_belief: new dict of node belief 
        @type node_belief: dict
        
        @param root_set: ground truth node set
        @type root_set: list
        
        @return: accuracy
        @return: f_score
        """
        x = []
        y = []
        d = []
        for node in node_label:
            if node in root_set:
                pass
            else:
                d.append(node)
                if node_label[node] == "d":
                    x.append(1)
                else:
                    x.append(0)
                if node_belief[node][0] > node_belief[node][1]: # democrat
                    y.append(1)
                elif node_belief[node][0] < node_belief[node][1]: # republican
                    y.append(0)
                else: # in this case, we don't have belief orientation; thus, random guess or don't judge
                    ### random guess
                    r = random.random()
                    if r < 0.5:
                        y.append(1)
                    else:
                        y.append(0)
                    ### don't judge them
                    """if node_label[node] == "d":
                        y.append(0)
                    else:
                        y.append(1)"""
        try:
            accuracy = metrics.accuracy_score(x, np.array(y))
            f_score = metrics.f1_score(x, np.array(y))
        except:
            accuracy = 0.0
            f_score = 0.0
        print "  ", accuracy, f_score
        return accuracy, f_score
        
        
    
    def cross_validation(self, iter = 10, fold = 10):
        """
        @description: {train_percent} of ground truth with BP algo.
                        Save to file
        @note: [val1, val2] all tuples like this indicates that val1-democ. prob.; val2-repul. prob.
        
        @param iter: number of iteration
        @type iter: int. typically 10, 20
        
        @param fold: folding
        @type fold: int. typically 10, 8, 5, 4, 2
        """
        f = open("../results/results_fscore_accuracy_feb23_bp/bp_result_rg_%dfold.csv" %fold,"w")
        f.write("iter,f_score,accuracy\n")
        for i in range(iter):
            #print len(self.G.edges()), self.G.edges()
            nodes = list(self.G.nodes())
            random.shuffle(nodes) # shuffle the list for every iteration
            trunk_size = len(nodes)/fold
            a = 0.0
            s = 0.0
            for j in range(fold):
                root_set = []
                if j != trunk_size-1:
                    root_set.extend(nodes[j*trunk_size:(j+1)*trunk_size])
                else:
                    root_set.extend(nodes[j*trunk_size:len(nodes)])
                nodes_belief = dict.fromkeys(self.G.nodes(), [0.5, 0.5])
                for node in root_set:
                    if self.nodes_label[node] == "d":
                        nodes_belief[node] = [0.99, 0.01]
                    else:
                        nodes_belief[node] = [0.01, 0.99]
                edge_messages = self.initialize_messages(self.G)
                t1 = time.time()
                new_nodes_belief, edge_messages = beliefprop(self.G, edge_messages, nodes_belief)
                t2 = time.time()
                print "fold%d-iter%d: %.2fs" %(fold, j, (t2-t1)),
                """evaluation"""
                accuracy, f_score = self.evaluation(self.nodes_label, new_nodes_belief, root_set)
                f.write("f%d,%f,%f\n" %(j, accuracy, f_score))
                a += accuracy
                s += f_score
            f.write("i%d,%f,%f\n" %(i, a/float(fold), s/float(fold)))
            f.write("\n")
        f.close()

    def initialize_messages(self, G):
        """
        @description: initialize messages
        @note: [val1, val2] all tuples like this indicates that val1-democ. prob.; val2-repul. prob.
        
        @param G: graph
        @type G: networkx DiGraph
        
        @return: a dict of edge messages
        """
        edge_messages = {}
        edges = G.edges()
        for edge in edges:
            edge_messages.update({edge[0]+"#"+edge[1] : [1.0, 1.0]})
        return edge_messages

def main():
    mybp = bp()
    mybp.read_graph("../../social_analysis/user_graph/user_graph_393_screen_name_2.txt")
    folds = [2, 4, 5, 8, 10, 20, 50]
    for i in range(len(folds)):
        mybp.cross_validation(5, folds[i])
        print
    
    
if __name__ == "__main__":
    main()
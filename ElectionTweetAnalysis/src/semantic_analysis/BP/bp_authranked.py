"""
@description: this program rank the nodes using in_degree and use nodes with
the largest in_degree as the root set
@author: Bolun Huang
"""

"""
@description: this program implement the bayes-based belief propagation
with the aim to improve belief propagation inference
@author: Bolun Huang
"""
import bp_authbased as bp
import cjson   
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

class bayes_bp:
    def __init__(self):
        self.mybp = bp.bp()
        self.mybp.read_graph("../../social_analysis/user_graph/user_graph_393_screen_name_2.txt")
        ### mybp.G - graph
        ### mybp.nodes_label - node labels
        f = open("../results/sentiscore_vectors_1/adjusted_sentiscore_vector_1.0_0-39.json", "r")
        self.vector = cjson.decode(f.readline()) ### feature vector
        f.close()
    
    def cross_validation(self):
        folds = [50,20,10,8,5,4,2] # folds to be used
        f = open("../results/results_fscore_accuracy_feb28_bp/bp_authranked_rg.csv","w")
        f.write("authranked_bp\n")
        f.write("iter,fscore,accuracy\n")
        for fold in folds:
            accuracy, fscore = self.run_bayes_bp(fold)
            f.write("f%d,%f,%f\n" %(fold,fscore,accuracy))
        
        f.close()
    
    def run_bayes_bp(self, fold = 10):
        nodes_with_in_degree = []
        for node in self.mybp.G.nodes():
            nodes_with_in_degree.append([node, self.mybp.G.in_degree(node)])
        
        nodes = sorted(nodes_with_in_degree, key = lambda x : x[1], reverse = True)
        trunk_size = len(nodes)/fold

        train_ids = [node[0] for node in nodes[0:trunk_size]]
        test_ids = [node[0] for node in nodes[trunk_size:]]
        
        fscore = 0.0
        accuracy = 0.0
        
        """apply Belief Propagation"""
        nodes_belief = dict.fromkeys(self.mybp.G.nodes(), [0.5, 0.5])
        for node in train_ids:
            if self.mybp.nodes_label[node] == "d":
                nodes_belief[node] = [0.99, 0.01]
            else:
                nodes_belief[node] = [0.01, 0.99]
        
        edge_messages = self.mybp.initialize_messages(self.mybp.G)
        new_nodes_belief, edge_messages = bp.beliefprop(self.mybp.G, edge_messages, nodes_belief)
        accuracy, fscore = self.mybp.evaluation(self.mybp.nodes_label, new_nodes_belief, train_ids)
        print "\tbayes_based_bp: ", accuracy, fscore
        return accuracy, fscore
    
    def toList(self, dict = {}):
        rList = []
        for key in dict:
            rList.append(dict[key])
        return rList

def main():
    folds = [2, 4, 5, 8, 10, 20, 50] # folds to be used
    mybb = bayes_bp()
    mybb.cross_validation()

if __name__ == "__main__":
    main()
    

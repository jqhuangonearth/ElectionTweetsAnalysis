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
        folds = [50] # folds to be used
        for fold in folds:
            self.run_bayes_bp(fold, 3)
    
    def run_bayes_bp(self, fold = 10, iters = 5):
        nodes = list(self.mybp.G.nodes())
        f = open("../results/results_fscore_accuracy_feb27_bp/bp_result_bayes_adjusted_%dfold.csv" %fold,"w")
        f.write("bayes_based_bp,bayes_adjusted_bp\n")
        f.write("iter,bayes_adjusted_bp_fscore,bayes_adjusted_bp_accuracy,bayes_fscore,bayes_accuracy\n")
        for iter in range(iters):
            random.shuffle(nodes) # shuffle the list for every iteration
            trunk_size = len(nodes)/fold
            
            mean_fscore_bayes = 0.0
            mean_accuracy_bayes = 0.0
            mean_fscore_bayes_adjusted_bp = 0.0
            mean_accuracy_bayes_adjusted_bp = 0.0
            
            for i in range(fold):
                print "iter %d  " %i
                train_ids = []
                test_ids = []
                for j in range(fold):
                    if j == i:
                        if j == fold-1:
                            train_ids.extend(nodes[j*trunk_size:len(nodes)])
                        else:
                            train_ids.extend(nodes[j*trunk_size:(j+1)*trunk_size])
                    else:
                        if j == fold-1:
                            test_ids.extend(nodes[j*trunk_size:len(nodes)])
                        else:
                            test_ids.extend(nodes[j*trunk_size:(j+1)*trunk_size])
                
                """apply Naive Bayes"""
                train_x = []
                train_Y = []
                test_x = []
                test_Y = []
                for id in train_ids:
                    train_x.append(self.toList(self.vector[id]))
                    if self.mybp.nodes_label[id] == "d":
                        train_Y.append(1)
                    else:
                        train_Y.append(0)
                for id in test_ids:
                    test_x.append(self.toList(self.vector[id]))
                    if self.mybp.nodes_label[id] == "d":
                        test_Y.append(1)
                    else:
                        test_Y.append(0)
                clf = GaussianNB()
                clf.fit(train_x, train_Y)
                y_predicted = clf.predict(test_x)
                y_predicted_prob = clf.predict_proba(test_x)
                print y_predicted_prob
                
                f_score_bayes = metrics.f1_score(test_Y, y_predicted)
                accuracy_bayes = metrics.accuracy_score(test_Y, y_predicted)
                mean_fscore_bayes += f_score_bayes
                mean_accuracy_bayes += accuracy_bayes
                print "\tnaive bayes: ", accuracy_bayes, f_score_bayes
                
                """apply bayes_adjusted Belief Propagation"""
                nodes_belief = dict.fromkeys(self.mybp.G.nodes(), [0.5, 0.5])
                for node in train_ids:
                    if self.mybp.nodes_label[node] == "d":
                        nodes_belief[node] = [0.99, 0.01]
                    else:
                        nodes_belief[node] = [0.01, 0.99]
                edge_messages = self.mybp.initialize_messages(self.mybp.G)
                new_nodes_belief, edge_messages = bp.beliefprop(self.mybp.G, edge_messages, nodes_belief)
                predicted_prob = {}
                for k in range(len(test_ids)):
                    predicted_prob.update({test_ids[k] : y_predicted_prob[k]})
                accuracy_bayes_adjusted_bp, fscore_bayes_adjusted_bp = self.evaluate(self.mybp.nodes_label, 
                                                                                     new_nodes_belief, 
                                                                                     train_ids, 
                                                                                     predicted_prob)
                mean_accuracy_bayes_adjusted_bp += accuracy_bayes_adjusted_bp
                mean_fscore_bayes_adjusted_bp += fscore_bayes_adjusted_bp
                print "\tbayes_adjusted_bp: ", accuracy_bayes_adjusted_bp, fscore_bayes_adjusted_bp
                
                f.write("f%d,%f,%f,%f,%f\n" %(i, fscore_bayes_adjusted_bp, accuracy_bayes_adjusted_bp,
                                                    f_score_bayes, accuracy_bayes))
            f.write("i%d,%f,%f,%f,%f\n" %(iter, mean_fscore_bayes_adjusted_bp/float(fold), 
                                                mean_accuracy_bayes_adjusted_bp/float(fold),
                                                mean_fscore_bayes/float(fold), 
                                                mean_accuracy_bayes/float(fold)))
        f.close()
        
    def evaluate(self, node_label = {}, node_belief = {}, train_ids = [], predicted_prob = {}):
        """
        @description: use bayes model to adjust belief propagation
        if bp renders the same prediction with bayes, then stick to bp;
        if bp renders different prediction with bayes, stick to bp as well;
        if bp renders [0.5, 0.5], then stick to bayes model.
        
        @param node_label: dict of node belief
        @type node_label: dict
        
        @param node_belief: new dict of node belief 
        @type node_belief: dict
        
        @param train_ids: ground truth node set
        @type train_ids: list
        
        @param predicted_prob: bayes predicted result
        @type predicted_prob: dict
        
        @return: accuracy
        @return: f_score
        """
        x = [] # ground truth
        y = [] # predicted
        d = []
        accuracy = 0.0
        f_score = 0.0
        for node in node_label:
            if node in train_ids:
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
                else: # in this case, we stick to the bayes model
                    if predicted_prob[node][0] > predicted_prob[node][1]:
                        y.append(0)
                    else:
                        y.append(1)
        try:
            accuracy = metrics.accuracy_score(x, np.array(y))
            f_score = metrics.f1_score(x, np.array(y))
        except:
            print "except", 
            accuracy = 0.0
            f_score = 0.0
        return accuracy, f_score
    
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
    

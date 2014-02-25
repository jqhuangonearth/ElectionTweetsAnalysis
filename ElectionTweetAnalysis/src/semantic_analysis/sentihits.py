"""
This program implements Hyperlink-Induced Topic Search in social graph
mixed with sentiment score for a particular topic
This method adjusted the sentiscore at the final step with auth(U)
and sentihits_adjusted.py is adjusting scores in each steps
@author: Bolun hbl080212(at)neo(dot)tamu(dot)edu
@reference: http://code.google.com/p/python-graph/issues/detail?id=113
@copyright: http://code.google.com/p/python-graph/issues/detail?id=113
@copyright: Free to use
@author: Bolun Huang
"""
import networkx as nx
import matplotlib.pyplot as plt
import cjson
import gzip
import json
from pymongo import Connection

# mongodb parameter
DB_SERVER = "localhost"
DB_PORT = 27017
DB_NAME = "electiontweetsanalysis"
COLLECTION_UV = "user_vector_campainers"

connection = Connection(DB_SERVER, DB_PORT)
db = connection[DB_NAME]

# TODO: subject to future change
"""keywords = ["tcot", "syria", "p2", "bengahazi", "obama",
            "teaparty", "uniteblue", "gop", "obamacare",
            "tlot", "pjnet", "lnyhbt", "tgdn", "israel",
            "ccot", "romney", "nra", "nsa", "irs"]
"""
keywords = []

def get_keyword_vector():
    ff = open("results/statistics_hashtag_sentiscores_78.csv","r")
    keywords_feature_vector = {}
    features = []
    line = ff.readline()
    line = line.split(";")
    for f in line[1:]:
        features.append(f.rstrip())

    for line in ff:
        line = line.split(";")
        vals = line[1:]
        keywords_feature_vector.update({line[0] : {}})
        keywords_feature_vector[line[0]].update({features[i] : float(vals[i]) for i in range(len(vals))})
    ff.close()
    
    """sorted by sentiscore_diff"""
    #keywords_feature_vector_list = sorted(keywords_feature_vector.iteritems(), key = lambda x : x[1]["sc_min_max_diff"], reverse = True)
    """sorted by sentiword_diff"""
    keywords_feature_vector_list = sorted(keywords_feature_vector.iteritems(), key = lambda x : x[1]["sw_min_max_diff"], reverse = True)
    #keywords = [kw[0] for kw in keywords_feature_vector_list[0:len(keywords_feature_vector_list)/2]]
    #keywords = [kw[0] for kw in keywords_feature_vector_list[len(keywords_feature_vector_list)/2:len(keywords_feature_vector_list)]]
    """divide into top10, mid10 and last10"""
    """top10"""
    #keywords = [kw[0] for kw in keywords_feature_vector_list[0:10]]
    """middle10"""
    #keywords = [kw[0] for kw in keywords_feature_vector_list[len(keywords_feature_vector_list)/2:len(keywords_feature_vector_list)/2+10]]
    """last10"""
    #keywords = [kw[0] for kw in keywords_feature_vector_list[len(keywords_feature_vector_list)-10:len(keywords_feature_vector_list)]]
    
    """top5"""
    #keywords = [kw[0] for kw in keywords_feature_vector_list[0:5]]
    """middle5"""
    #keywords = [kw[0] for kw in keywords_feature_vector_list[len(keywords_feature_vector_list)/2:len(keywords_feature_vector_list)/2+5]]
    """last5"""
    keywords = [kw[0] for kw in keywords_feature_vector_list[len(keywords_feature_vector_list)-5:len(keywords_feature_vector_list)]]
    """
    f = open("results/features_last5.json","w")
    json.dump(keywords, f)
    f.close()
    exit(0)
    """
    return keywords
    
def sentihits(graph, root_set=[], keyword = "", max_iterations=100, min_delta=0.0001):
    """
    Compute and return the PageRank in an directed graph. We assume that the
    source node points to the target node according to the links.

    @type  graph: digraph
    @param graph: Digraph

    @type  root_set: list
    @param root_set: The most relevant pages to the search query

    @type keyword: string
    @param keyword: keyword e.g. "obama"

    @type  max_iterations: number
    @param max_iterations: Maximum number of iterations.

    @type  min_delta: number
    @param min_delta: Smallest variation required to have a new iteration.

    @rtype: dictionary
    @return:  dict of adjusted_senti_score for keyword
    """

    # extend root set by appending all the pages that point or are pointed
    # by the rott set
    base_set = []
    if not root_set:
        base_set = graph.nodes()
    else:
        base_set = []
        for node in root_set:
            for nod in graph.node_incidence[node]:
                base_set.append(nod)
        for node in root_set:
            for nod in graph.node_neighbors[node]:
                base_set.append(nod)
        base_set.extend(root_set)
        base_set = set(base_set)

    auth = dict.fromkeys(base_set, 1)
    hub = dict.fromkeys(base_set, 1)
    
    base_senti_score = get_base_sentiscore(base_set, keyword)
    print "done keyword: %s" %keyword
    # normal HITS algorithm
    i = 0
    for i in range(max_iterations):
        for p in base_set:
            hub_list = [hub.get(q[0]) for q in graph.in_edges(p)] # sum of hub_score of its followers
            auth[p] = sum(hub_list)

        auth = normalize(auth)

        old_hub = dict()
        for p in base_set:
            old_hub[p] = hub[p]
            auth_list = [auth.get(r[1]) for r in graph.out_edges(p)] # sum of auth_score of its friends
            hub[p] = sum(auth_list)

        hub = normalize(hub)
        # testing whether the error is less than the given delta
        delta = sum((abs(old_hub[k] - hub[k]) for k in hub))
        if delta <= min_delta:
            break
    
    adjusted_senti_score = {}
    alpha = 0.91 # branching factor
    # adjust the scores in the base_senti_score
    for user in base_senti_score:
        new_senti_score = 0.0
        auth_list = [auth.get(r[1]) for r in graph.out_edges(user)]
        base_score_list = [base_senti_score.get(r[1]) for r in graph.out_edges(user)]
        sigma = 0.0
        for i in range(len(auth_list)):
            sigma += auth_list[i]*base_score_list[i]
        if len(auth_list) > 0:
            new_senti_score = alpha*base_senti_score[user]+(1-alpha)*(sigma/float(len(auth_list)))
        else:
            new_senti_score = base_senti_score[user]
        adjusted_senti_score.update({user : new_senti_score})
    return adjusted_senti_score
        
def get_base_sentiscore(user_list, item):
    """
    given a term, calculate and retrieve the sentiment score of that term
    for a list of user
    @param user_list: list of user in screen_name
    @param item: keyword
    @return user_base_score: a dict of base sentiment scores for each user in user_list
    """
    user_base_score = {}
    for user in user_list:
        score = 0.0
        count = 0
        it = db[COLLECTION_UV].find({"screen_name" : user})
        for i in it:
            for tweet in i["tweets"]:
                if item in tweet["text"]:
                    if not tweet["sentiment_score"] == None and not tweet["sentiword_score"] == None:
                        if not (tweet["sentiment_score"] < 0.01 and tweet["sentiment_score"] > -0.01) and not (tweet["sentiword_score"] < 0.01 and tweet["sentiword_score"] > -0.01):
                            score += (tweet["sentiment_score"] + tweet["sentiword_score"])/2.0
                            count += 1
        if not count == 0:
            score = score/float(count)
        else:
            score = 0.0
        user_base_score.update({user : score})
    return user_base_score


def normalize(dictionary):
    length = len(dictionary)
    """ Normalize the values of a dictionary to sum up to 1. """
    norm = sum((dictionary[p] for p in dictionary))
    if norm!=0:
        return {k: (v / float(norm))*length for (k, v) in dictionary.items()}
    else:
        return {k: v for (k, v) in dictionary.items()}
    

def draw_graph(G):
    """
    @type G: DiGraph
    @param G: DiGraph
    """
    nx.draw(G, pos = nx.random_layout(G, dim = 2), randomcmap = plt.get_cmap('jet'), node_color = "blue", alpha = 0.5, width = 1, node_size = 200, with_labels=False)
    plt.show()


class hits_test():
    def __init__(self, keyword_list = []):
        self.G = nx.DiGraph() # internal graph
        self.keyword_list = keyword_list
        
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
    
    def find_lone_node(self):
        f = open("data/lonely_nodes_list.txt","w")
        f.write("#to be removed since they doesn't have connections in this local graph")
        for n in self.G:
            if self.G.degree(n) == 0:
                #print n
                f.write(n+"\n")
        f.close()
        
    def run_sentihits(self):
        return sentihits(self.G)
    
    def test_sentihits(self):
        adjusted_score_vector = {}
        
        for keyword in self.keyword_list:
            user_senti_score_dic = sentihits(self.G, keyword = keyword) # run sentihits to get adjusted sentiment score
            for user in user_senti_score_dic:
                if user not in adjusted_score_vector:
                    adjusted_score_vector.update({user : {keyword : user_senti_score_dic[user]}})
                else:
                    adjusted_score_vector[user].update({keyword : user_senti_score_dic[user]})
        f = open("results/sentiscore_vectors_2/5features/adjusted_sentiscore_vector_0.91_last5.json","w")
        json.dump(adjusted_score_vector, f)
        f.close()
        
def main():
    #pre_process()
    #process_user_graph()
    keywords = get_keyword_vector()
    print keywords
    print len(keywords)

    ht = hits_test(keyword_list = keywords)

    fg = open("../social_analysis/user_graph/user_graph_393_screen_name_2.txt", "r")
    flag = 0
    node_list = []
    edge_list = []
    for line in fg:
        if flag == 1 and not line.startswith("#"):
            try:
                nodes = line.split(" ")
                node_list.append(nodes[0].rstrip())
            except:
                pass
        elif flag == 2 and not line.startswith("#"):
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
    print len(node_list), len(edge_list)
    ht.construct_graph(node_list, edge_list)
    print len(ht.G.nodes()), len(ht.G.edges())
    
    ht.find_lone_node()
    exit(0)
    ht.test_sentihits()
    #auth_score = hub_auth[1]
    #f = open("../social_graph/authorities.json","w")
    #json.dump(auth_score, f)
    #f.close()
    #print sorted(hub_auth[1].iteritems(), key=lambda asd:asd[1], reverse = False) # sort dic as list
    #print "hub_scores ", hub_auth[0]
    #print "auth_scores", hub_auth[1]
    
    
    
if __name__ == "__main__":
    main()
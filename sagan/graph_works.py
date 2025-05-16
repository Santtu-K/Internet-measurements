import pickle
from ripe.atlas.sagan import TracerouteResult
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


# load raw graph object from file
filename = '100graph.pickle'
G = pickle.load(open('100graph.pickle', 'rb'))
#nx.draw(G, with_labels=True, font_weight='bold')

degrees = [[int(asn),deg] for asn, deg in G.degree()]

# Prune scores for all ASns/nodes
prune_scores_list = [[int(n),1] for n in G]
prune_scores = dict(prune_scores_list)

# Prune the graph and calculate the Prune scores
flag = True
while flag == True:
    flag = False

    for i, x in enumerate(degrees):
        asn_i = x[0]
        degree = x[1]

        if degree <= 1:
            if degree == 1: # accumulate the prune score
                r = list(G.edges(asn_i))
                if len(r) > 0:
                    #print("hello asn:",asn_i, "edge",r, "type", type(r), "len", len(r))
                    a = dict(r)
                    source = a[asn_i]
                    prune_score = prune_scores[asn_i]
                    prune_scores[source] = prune_scores[source] + prune_score

            G.remove_node(asn_i)
            flag = True

    degrees = [[int(asn),deg] for asn, deg in G.degree()]

# Prune scores for only the "important" ASns/nodes (the ones that are left after pruning)
important_nodes_list = [(int(n), prune_scores[n]) for n in G]
important_nodes = dict(important_nodes_list)

# THESE ARE FOR THE PRUNED GRAPH

#  histogram 
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=range(1, max(degrees)+2), edgecolor='black', color='skyblue')
plt.title("Distribution of Node Degrees in ASN Graph")
plt.xlabel("Degree (Number of Connections)")
plt.ylabel("Number of ASNs")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


from collections import defaultdict
import random

all_nodes = list(G.nodes()) # convert nodes to a list
num_nodes = len(all_nodes)
num_samples = 1000  #Total  Number of random node pairs to pick to find shortest path

# Score: how many times each node appears in the middle of shortest paths
score = defaultdict(int) # empty dictionary to keep count how many times the nodes apprears

for _ in range(num_samples):
    src, dst = random.sample(all_nodes, 2)# picking nodes
    try:
        path = nx.shortest_path(G, source=src, target=dst)#finding shortest path between the 2
        for node in path[1:-1]:  # skip first and last
            score[node] += 1
    except nx.NetworkXNoPath:
        continue  # no path between this pair, skip that pair and continues

used_nodes = len(score) #how many nodes were used
all_scores = list(score.values()) #list of all score 

print(f"\nTotal nodes in graph: {num_nodes}")
print(f"Nodes used in paths (score ≥ 1): {used_nodes}")

# top asn with high score help us know important asns or central asns
top = sorted(score.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 nodes by score:")
for node, val in top:
    print(f"Node {node} → {val}")

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(all_scores, bins=30, edgecolor='black', color='skyblue')
plt.title("Node Path Score Histogram")
plt.xlabel("Times appeared in shortest paths")
plt.ylabel("Number of nodes")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()



nx.draw(G, with_labels=True, font_weight='bold')

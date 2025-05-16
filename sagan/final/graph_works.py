import pickle
from ripe.atlas.sagan import TracerouteResult
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import functions as func
import itertools
import random


# load raw graph object from file
filename = '2500graph.pickle'
G = pickle.load(open(filename, 'rb'))
#nx.draw(G, with_labels=True, font_weight='bold')

degrees = [[int(asn),deg] for asn, deg in G.degree()]

nx.draw(G, with_labels=True, font_weight='bold')
plt.show()
# Prune scores for all ASns/nodes
prune_scores_list = [[int(n),1] for n in G]
prune_scores = dict(prune_scores_list)

# Prune the graph and calculate the Prune scores
flag = True
while flag == True:
    flag = False

    for _, x in enumerate(degrees):
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



#print(allocated_ips)


# THESE ARE FOR THE PRUNED GRAPH
asns = [int(x) for x in G]
sorted_asns = sorted(asns)

allocated_ips = {}
for i, x in enumerate(G):
    asn = int(x)
    n_ip = func.get_total_allocatable_ips(asn)
    allocated_ips[asn] = n_ip

# bar chart: IP
x_asn_ip = [str(asn) for asn in sorted_asns]
y_path_score_ip = [allocated_ips[asn] for asn in sorted_asns]

plt.figure(figsize=(10, 6))
plt.bar(x_asn_ip, y_path_score_ip, color='skyblue', edgecolor='black')
plt.xticks(x_asn_ip)
plt.title("Distribution of number of allocated IPv4 @s by ASns")
plt.xlabel("ASn")
plt.ylabel("# of allocated IPv4 @s")
plt.yscale('log')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# degree part
degrees = [deg for _, deg in G.degree()]
#print(degrees)

# bar chart: degree
from collections import Counter

degree_counts = Counter(degrees)
sorted_counts = sorted(degree_counts.items())
x = [deg for deg, _ in sorted_counts]
y = [count for _, count in sorted_counts]

plt.figure(figsize=(10, 6))
plt.bar(x, y, color='skyblue', edgecolor='black')
plt.xticks(x)
plt.title("Distribution of Node Degrees in ASN Graph")
plt.xlabel("Degree")
plt.ylabel("Number of ASNs")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Path scores
all_nodes = list(G.nodes()) # convert nodes to a list
num_nodes = len(all_nodes)
num_samples = min(num_nodes**num_nodes, 10^6)  #Total  Number of random node pairs to pick to find shortest path

pairs = list(itertools.combinations(all_nodes, 2))
random.shuffle(pairs)
n_pairs = pairs[1:num_samples]

path_scores = {}

for asn in G:
    path_scores[int(asn)] = 1

for pair in n_pairs:
    src, dst = pair
    try:
        path = nx.shortest_path(G, source=src, target=dst)#finding shortest path between the 2
        for node in path[1:-1]:  # skip first and last
            path_scores[node] += 1
    except nx.NetworkXNoPath:
        continue  # no path between this pair, skip that pair and continues
all_path_scores = list(path_scores.values()) #list of all score 

# # top asn with high score help us know important asns or central asns
top = sorted(path_scores.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 nodes by score:")
for node, val in top:
    print(f"ASn {node} → {val}")

# bar chart: path score
x_asn = [str(asn) for asn in sorted_asns]
y_path_score = [path_scores[asn] for asn in sorted_asns]

plt.figure(figsize=(10, 6))
plt.bar(x_asn, y_path_score, color='skyblue', edgecolor='black')
plt.xticks(x_asn)
plt.title("Distribution of path scores of ASns")
plt.xlabel("ASn")
plt.ylabel("Path score")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()



# bar chart: prune score
x_prune = [str(asn) for asn in sorted_asns]
y_prune = [important_nodes[asn] for asn in sorted_asns]

plt.figure(figsize=(10, 6))
plt.bar(x_prune, y_prune, color='skyblue', edgecolor='black')
plt.xticks(x_prune)
plt.title("Distribution of prune scores of ASns")
plt.xlabel("ASn")
plt.ylabel("Prune score")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

nx.draw(G, with_labels=True, font_weight='bold')
plt.show()

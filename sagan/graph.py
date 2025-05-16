import requests
from ripe.atlas.sagan import TracerouteResult
import numpy as np
import pyasn
import networkx as nx
import matplotlib.pyplot as plt
import time 

asndb = pyasn.pyasn('ipasn_db.dat')
G = nx.Graph()

page_size = 100
stop = int(time.time()) # time now
start = stop - 86400 # time yesterday
hour = 60*60
starts = 

url = f"https://atlas.ripe.net/api/v2/measurements/?type=traceroute&status=4&start_time__gte={start}&page_size={page_size}&is_oneoff=True"
response = requests.get(url)
print(response.raise_for_status())
data = response.json()
res = [m['id'] for m in data['results']]
measurement_ids = np.array(res)
print(measurement_ids.size)
print(measurement_ids.shape)



arr_np = np.array(measurement_ids)
#print("Tried to found %d measurements, in the end, found %d measurements" % (n_measurement, arr_np.size))

for measurement_id in measurement_ids:
    source = 'https://atlas.ripe.net/api/v2/measurements/' + str(measurement_id)+ '/results/'
    response = requests.get(source)
    data = response.json()

    for x in data:
        parsed = TracerouteResult(x)
        path_ip = parsed.ip_path

        asn_paths = []

        for i, hop in enumerate(path_ip): # Iterate through the hops of a traceroute
            #filter IP None values
            hop = [x for x in hop if x is not None]
            hop = [x for x in hop if x != 'None']
            
            new_hop = [] # ASn(s) in the hop
            for j, ip in enumerate(hop):
                asn = asndb.lookup(ip)[0] # Get ASN for IP
                if asn is not None and asn != 'None': # ASN not a None value
                    if asn not in new_hop:
                        new_hop.append(asn) 
            
            n_asn = len(new_hop) # Number of ASns in the hop
            
            if n_asn > 1: # Save all paths and end here
                asn_paths.append(new_hop)
                break
            elif n_asn == 1:
                asn = new_hop[0]
                asn_paths.append(asn)

        path_size = len(asn_paths)

        if path_size > 0: # Non empty path
            last_elem = asn_paths[-1]
            
            if isinstance(last_elem, int) == False: # A hop contained multiple ASns
                if len(last_elem) > 1: 
                    print("A hop contained multiple ASns")
                    flat_path = [asn_paths[0]]
                    for i in range(1, path_size - 1): # Flatten the path --> No consecutive same ASNs in the path
                        x = asn_paths[i]
                        last_elem = flat_path[-1]
                        if x == last_elem:
                            continue
                        else:
                            flat_path.append(x)

                    flat_path = np.array(flat_path)
                    flat_path_size = flat_path.size

                    last_flat_path = flat_path[-1]

                    last_elem = asn_paths[-1]
                    G.add_node(flat_path[0])
                    for i in range(1, flat_path_size):
                        prev = flat_path[i-1]
                        asn = flat_path[i]
                        G.add_node(asn)
                        G.add_edge(asn, prev)
                    for _, asn in last_elem:
                        G.add_node(asn)
                        G.add_edge(asn, last_flat_path)
            else: # Every hop had exactly one ASn
                flat_path = [asn_paths[0]]
                for i in range(1, path_size): # Flatten the path --> No consecutive same ASNs in the path
                    x = asn_paths[i]
                    last_elem = flat_path[-1]
                    if x == last_elem:
                        continue
                    else:
                        flat_path.append(x)

                flat_path = np.array(flat_path)
                flat_path_size = flat_path.size
                G.add_node(flat_path[0])
                for i in range(1, flat_path_size):
                    prev = flat_path[i-1]
                    asn = flat_path[i]
                    G.add_node(asn)
                    G.add_edge(asn, prev)

nx.draw(G, with_labels=True, font_weight='bold')
plt.show()

import pickle

# save graph
file_name = '500graph.pickle'
pickle.dump(G, open(file_name, 'wb'))
import requests  
from ripe.atlas.sagan import TracerouteResult
import numpy as np
import pyasn
import networkx as nx
import matplotlib.pyplot as plt

def fetch_traceroute_ids_from_base_api(limit=5):
    """
    Fetch recent completed traceroute measurement IDs from RIPE Atlas.
    """
    url = f"https://atlas.ripe.net/api/v2/measurements/?type=traceroute&status=2&is_oneoff=true&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return [m['id'] for m in data['results']]

def process_traceroutes(measurement_ids, ipasn_path='ipasn_db.dat'):
    asndb = pyasn.pyasn(ipasn_path)
    G = nx.Graph()

    for measurement_id in measurement_ids:
        url = f'https://atlas.ripe.net/api/v2/measurements/{measurement_id}/results/'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for result in data:
            parsed = TracerouteResult(result)
            ip_path = parsed.ip_path  # This is a list of lists (per-hop attempts)

            if not ip_path:
                continue

            # Flatten IPs per hop (remove None), then collect first successful IP per hop
            path_asns = []
            for hop in ip_path:
                valid_ips = [ip for ip in hop if ip is not None]
                if not valid_ips:
                    continue
                ip = valid_ips[0]  # Take the first successful try
                asn = asndb.lookup(ip)[0]
                if asn is not None:
                    if len(path_asns) == 0 or path_asns[-1] != asn:
                        path_asns.append(asn)

            for i in range(1, len(path_asns)):
                G.add_edge(path_asns[i-1], path_asns[i])

    return G


def draw_and_save_graph(G, filename='as_graph.png'):
    """
    Draw and save the AS graph to a PNG file.
    """
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # Consistent layout
    nx.draw(G, pos, with_labels=True, node_size=500, font_size=8, font_weight='bold')
    plt.title("Autonomous System (AS) Graph from Traceroute Data")
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Graph saved as: {filename}")
    plt.show()

if __name__ == "__main__":
    print("Fetching traceroute IDs from RIPE Atlas base API...")
    measurement_ids = fetch_traceroute_ids_from_base_api(limit=5)
    print("Fetched measurement IDs:", measurement_ids)

    G = process_traceroutes(measurement_ids)
    draw_and_save_graph(G)

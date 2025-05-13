import requests
from ripe.atlas.sagan import Result
from ripe.atlas.sagan import TracerouteResult
import numpy as np
from aslookup import get_as_data
import pyasn

asndb = pyasn.pyasn('ipasn_db.dat')

measurement_id = 100274119
source = 'https://atlas.ripe.net/api/v2/measurements/' + str(measurement_id)+ '/results/'
#source = "https://atlas.ripe.net/api/v2/measurements/" + str(measurement_id)+ "/?is_public=true"
response = requests.get(source)
data = response.json()

print(type(data))

for x in data:
    print(x)
    parsed = TracerouteResult(x)

    print(parsed.hops)

    dest_ip = parsed.destination_address
    src_ip = parsed.source_address
    path_ip = parsed.ip_path

    arr = np.array(path_ip)

    path_1 = arr[:,0]
    path_size = path_1.size

    path_2 = arr[:,1]
    path_3 = arr[:,2]

    for idx, x in enumerate(path_1):
        print(idx, x) 
        asn = asndb.lookup(x)[0]
        path_1[idx] = asn
    
    flat_path_1 = [path_1[0]]
    for i in range(1, path_size - 1):
        x = path_1[i]
        last_elem = flat_path_1[-1]

        if x == last_elem:
            continue
        else:
            flat_path_1.append(x)

    flat_path_1 = list(filter(lambda x: x != 'None', flat_path_1)) # Remove NONE values
    flat_path_1 = np.array(flat_path_1) 
    print("original path", path_1)
    print("flat path", flat_path_1)
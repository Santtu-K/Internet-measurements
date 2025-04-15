import requests
import pandas as pd

url = 'https://atlas.ripe.net/api/v2/probes/?is_public=true'
all_probes = []

while url:
    print(f"Fetching: {url}")
    response = requests.get(url)
    data = response.json()
    all_probes.extend(data['results'])
    url = data['next']

df = pd.DataFrame(all_probes)
df.to_csv('public_probes.csv', index=False)
import requests
import json

url = "https://tld.iot.hamburg.de/v1.0/Things"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    
    print(json.dumps(data, indent=2))
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
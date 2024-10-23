#!/usr/bin/env python3
import json
import os
import requests

body = {"bbox":[[9.98, 53.54], [10.0, 53.56]]}

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': os.environ['ORS_API_KEY'],
    'Content-Type': 'application/json; charset=utf-8'
}
call = requests.post('https://api.openrouteservice.org/v2/export/driving-car', json=body, headers=headers)

print(json.dumps(json.loads(call.text), indent=4))

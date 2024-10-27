#!/usr/bin/env python3
"""Testing code to fetch a localized ORS graph and map it to OSM"""
import json
import os
import math
import requests

from models import ORSNode, OSMNode

body = {"bbox": [[9.82, 53.65], [10.21, 53.54]]}

headers = {
    "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
    "Authorization": os.environ["ORS_API_KEY"],
    "Content-Type": "application/json; charset=utf-8",
}
call = requests.post(
    "https://api.openrouteservice.org/v2/export/driving-car",
    json=body,
    headers=headers,
    timeout=5,
)

ors_data = json.loads(call.text)

with open("ors_graph.json", "w", encoding="utf-8") as fp:
    json.dump(ors_data, fp, indent=4)

ors_nodes = []

for node in ors_data["nodes"]:
    ors_nodes.append(
        ORSNode(node["nodeId"], lat=node["location"][1], lon=node["location"][0])
    )

distances = []
for i, ors_node in enumerate(ors_nodes[:50]):
    print("Getting OSM node #" + str(i))
    osm_node = OSMNode.from_ors(ors_node)
    distances.append(
        math.dist((osm_node.lat, osm_node.lon), (ors_node.lat, ors_node.lon))
    )


print(distances)
print("max distance: ", max(distances))

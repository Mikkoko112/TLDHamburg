#!/usr/bin/env python3
import folium
import json
import sys

filePath = sys.argv[1]
with open(filePath,"r") as file:
    data = json.load(file)

m = folium.Map(localtion = [9.99,53.55], zoom_start=4)
print()
for nodes in data['nodes']:
    print(nodes['location'])
    folium.Marker(
        nodes['location'][::-1],
        icon=folium.Icon(color='blue')
    ).add_to(m)

m.save("map.html")
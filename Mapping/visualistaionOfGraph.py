#!/usr/bin/env python3
import folium
import json
import sys

filePath = sys.argv[1]
with open(filePath,"r") as file:
    data = json.load(file)

m = folium.Map(localtion = [9.99,53.55], zoom_start=0.01)

colours = [
    "green", #ingress
    "orange", #route
    "red",  #exgress
    "black" #buffer
]

for nodes in data['nodes']:
    folium.Marker(
        nodes['location'][::-1],
        icon=folium.Icon(color='blue')
    ).add_to(m)

with open("./thingsLoc.json","r") as file:
    dataLanes = json.load(file)

length = len(dataLanes)

for n,lanes in enumerate(dataLanes):
    #print(lanes)
    if(n>=100):
        break
    print("{:.0f}%".format(100*(n/length)))
    for i,paths in enumerate(dataLanes[lanes]):
        #print(i,paths)
        if i == 1:
            for coords in paths:
                #print(coords)
                folium.Marker(
                    coords[::-1],
                    icon=folium.Icon(color=colours[i])
                ).add_to(m)


m.save("map.html")
#!/usr/bin/env python3
import folium
import json
import sys

filePath = sys.argv[1]
with open(filePath,"r") as file:
    lights = json.load(file)

filePath = sys.argv[2]
with open(filePath,"r") as file:
    areaData = json.load(file)


m = folium.Map(localtion = [9.99,53.55], zoom_start=0.01)

colours = [
    "green", #ingress
    "orange", #route
    "red",  #exgress
    "black" #buffer
]

for light in lights["23229"][1]:
    for i,li in enumerate(light[1][:3]):
        print(li)
        
        folium.Marker(
            location=li[::-1],
            icon=folium.Icon(color=colours[i])
        ).add_to(m)

for note in areaData["nodes"]:
    folium.Marker(
            location=note["location"][::-1],
            icon=folium.Icon(color='blue')
        ).add_to(m)
m.save("{}.html".format(sys.argv[3]))
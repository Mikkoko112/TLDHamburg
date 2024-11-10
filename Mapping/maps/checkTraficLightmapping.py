#!/usr/bin/env Python3


import folium
import json
import sys

filePath = sys.argv[1]
with open(filePath,"r") as file:
    data = json.load(file)

with open("../data/conjunctionsJoint.json","r") as file:
    conj = json.load(file)



m = folium.Map(localtion = [9.99,53.55], zoom_start=0.01)

if len(sys.argv) >= 4:
    fieldToVisualise = sys.argv[3]
else:
    fieldToVisualise = "23229"

colours = [
    "green", #ingress
    "orange", #route
    "red",  #exgress
    "black" #buffer
]

#erstmal die originalen conj
for name,dat in conj.items():
    coord = dat[0]
    print(data)
    if name in data['traficList']:
        color = "green"
    else:
        color = "red"
    if len(dat[1]) >1:
        rectangle = folium.Rectangle(
            bounds = [coord[0][::-1], coord[1][::-1]],
            color = color,
            fill=True,
            fill_color=color,
            fill_opacity=0.2,
            tooltip=name
        ).add_to(m)


#jetzt die neuen
for i,coord in enumerate(data['wayPoints'][:-1]):
    folium.PolyLine(
                [coord[::-1],data['wayPoints'][i+1][::-1]],
                color='yellow',
                weight=3
            ).add_to(m)



m.save("{}.html".format(sys.argv[2]))
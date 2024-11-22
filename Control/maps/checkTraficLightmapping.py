#!/usr/bin/env Python3


import folium
import json
import sys

filePath = sys.argv[1]
with open(filePath,"r") as file:
    data = json.load(file)

with open("../data/conjunctionsJoint.json","r") as file:
    conj = json.load(file)

with open("../data/vectorisation.json","r") as file:
    vect = json.load(file)



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
    if name in data['conjList']:
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
    
    
    
for vecAreaName,area in data['conjList'].items():
    for primary in conj[vecAreaName][1]:
        vec = vect[primary[0]]
        print(primary[0])
        if len(vec[0][0:2]) != 2: vec[0][0:2] = vec[1][::-1]
        if len(vec[2][0:2]) != 2: vec[2][0:2] = vec[1][::-1]

        lines= [
            [-x+y for x,y in zip(vec[0][0:2],vec[1][0:2])][::-1],
            vec[1][0:2][::-1],
            [x+y for x,y in zip(vec[2][0:2],vec[1][0:2])][::-1]
        ]
        folium.PolyLine(
            lines,
            color='orange',
            weight=2
        ).add_to(m)
        for i,note in enumerate(primary[1][0:3]):
            folium.Marker(
                location=note[::-1],
                icon=folium.Icon(color=colours[i])
            ).add_to(m)

for nameVec in data["traficLights"]:
    vec = vect[nameVec]
    if len(vec[0][0:2]) != 2: vec[0][0:2] = vec[1][::-1]
    if len(vec[2][0:2]) != 2: vec[2][0:2] = vec[1][::-1]

    lines= [
        [-x+y for x,y in zip(vec[0][0:2],vec[1][0:2])][::-1],
        vec[1][0:2][::-1],
        [x+y for x,y in zip(vec[2][0:2],vec[1][0:2])][::-1]
    ]
    folium.PolyLine(
        lines,
        color='darkred',
        weight=2
    ).add_to(m)





#jetzt die neuen
for i,coord in enumerate(data['wayPoints'][:-1]):
    folium.PolyLine(
                [coord[::-1],data['wayPoints'][i+1][::-1]],
                color='purple',
                weight=3
            ).add_to(m)




m.save("{}.html".format(sys.argv[2]))
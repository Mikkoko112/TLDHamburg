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


if(sys.argv[2] == "1"):
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

ind = 0
if(sys.argv[2]=="0"):
    for name,dat in data.items():
        ind +=1
        if ind > 15 and len(sys.argv)>=5: break
        coord = dat[0]
        if len(dat[1]) >1:
            rectangle = folium.Rectangle(
                bounds = [coord[0][::-1], coord[1][::-1]],
                color = 'orange',
                fill=True,
                fill_color="orange",
                fill_opacity=0.2,
                tooltip=name
            ).add_to(m)
            folium.Circle(
                location=dat[1][0][1][1][::-1],
                color="green",
                radius=2.2*1000,
                fill=True,
                fill_color="green",
                fill_opacity="0.1"
            ).add_to(m)
            if(len(sys.argv)>=5):
                for loc in dat[1]:
                    folium.Marker(
                        location=loc[1][1][::-1],
                    ).add_to(m)

m.save("{}.html".format(sys.argv[3]))
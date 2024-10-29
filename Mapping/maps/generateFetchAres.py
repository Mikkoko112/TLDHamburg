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


ind = 0
for name,dat in data.items():
    ind +=1
    if ind > 10 and sys.argv[3]=="1": break
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
            radius=2.2,
            fill=True,
            fill_color="green",
            fill_opacity="0.1"
        ).add_to(m)
        if(sys.argv[3]=="1" or name == "21736" or name == "23299" or name == "22472"):
            for loc in dat[1]:
                for i,locData in enumerate(loc[1][0:3]):
                    folium.Marker(
                        location=locData[::-1],
                        icon=folium.Icon(color=colours[i])
                    ).add_to(m)

m.save("{}.html".format(sys.argv[2]))
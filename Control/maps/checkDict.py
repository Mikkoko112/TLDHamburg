#!/usr/bin/env Python3

''' Dieses Skript funktioniert nur auf der alten Version von traficClass und war zur Validierung da.
    Diese Ergebnisse können nur mit einer alten Version von traficClass wiederholt werden, da die 
    Koordianten aus dem Dict entfernt wurden, um Speicher zu sparen und spätere Realtime-perationen
    auf diesem Dict zu ermöglichen.
    
    Eventuell wird hier noch eine debug möglichkeit eingefügt mit der -d operion'''

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

def generateLines(m):
    
    


#erstmal die originalen conj
for name,dat in conj.items():
    coord = dat[0]
    if name in data:
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
for name,dat in data.items():
    coord = dat["bound"]
    if True:
        rectangle = folium.Rectangle(
            bounds = [coord[0][::-1], coord[1][::-1]],
            color = 'orange',
            fill=True,
            fill_color="orange",
            fill_opacity=0.2,
            tooltip=name
        ).add_to(m)

        if(name == fieldToVisualise) or True:
            for loc in dat["junctionNodes"]:
            
                folium.Marker(
                    location=loc["location"][::-1],
                    icon=folium.Icon(color='darkred')
                ).add_to(m)






m.save("{}.html".format(sys.argv[2]))
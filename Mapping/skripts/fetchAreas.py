#!/usr/bin/env python3
import json
import requests
from math import floor,ceil,dist
from geopy import distance
from time import sleep

modif = 100

def roundValues(coords:list)->list:
   
    coordsCopy = list(coords)
    func = [floor,ceil]
    for i,c in enumerate(coordsCopy):
        for j,ax in enumerate(c):
            coordsCopy[i][j] = (func[i](ax*modif))/modif 
    return coordsCopy


def fetchAreas(relevantAres:dict):
    holeData = {}
    idx = 0
    for name, note in relevantAres.items():
        
        coords = note[0]
        holeData[name] = getNotes(roundValues(coords))
        print("{:.2f}% {} {}".format(idx/len(relevantAres)*100,len(holeData[name]),roundValues(coords)))
        idx+=1
        with open("holeData.json","w") as file:
            json.dump(holeData, file, indent=4)

        sleep(15)

    return holeData

def getNotes(coordsMinMax:list)->dict:
    body = {"bbox": coordsMinMax}
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf6248803978b4d3c14162a51793eab41b47c1",
        "Content-Type": "application/json; charset=utf-8",
    }
    call = requests.post(
        "https://api.openrouteservice.org/v2/export/driving-car",
        json=body,
        headers=headers,
        timeout=5,
    )

    return json.loads(call.text)

def mapPaths():
    with open("../data/outPutAreasSmallMin.json","r") as file:
        coords = json.load(file)

    areas = fetchAreas(coords)
    
    with open("holeData.json","w") as file:
        json.dump(areas, file, indent=4)

if __name__ == "__main__":
    mapPaths()
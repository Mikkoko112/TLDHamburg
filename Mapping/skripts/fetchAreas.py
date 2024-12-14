#!/usr/bin/env python3
import json
import requests
from math import floor,ceil,dist
from geopy import distance
from time import sleep

modif = 1000

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
        with open("holeData.json","w") as file: #after Run change
            json.dump(holeData, file, indent=4)

        sleep(15)

    return holeData

def getNotes(coordsMinMax:list)->dict:
    body = {"bbox": coordsMinMax}
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf62481657b4e645c0426a82d21a1932c60b2e",
        "Content-Type": "application/json; charset=utf-8",
    }
    call = requests.post(
        "https://api.openrouteservice.org/v2/export/driving-car",
        json=body,
        headers=headers,
        timeout=5,
    )

    return json.loads(call.text)

def singleCall():
    area = [
            [
                9.9733078,
                53.5440408
            ],
            [
                9.9930477,
                53.5644245
            ]
        ]
   
    areas = getNotes(area)

    with open("holeDataTest.json","w") as file:
        json.dump(areas, file, indent=4)
def mapPaths():
    with open("../data/outPutAreasSmallMin.json","r") as file:
        coords = json.load(file)

    areas = fetchAreas(coords)
    
    with open("holeData.json","w") as file:
        json.dump(areas, file, indent=4)

def getWrongSquares(coords:dict,coordsBase)->dict:
    out = dict()
    for name,coord in coords.items():
        if len(coord) != 4:
            out[name] = coordsBase[name]

    return out

def correctTheHoleData():
    with open("../data/outPutAreasSmallMin.json","r") as file:
        coordsBase = json.load(file)

    with open("holeData.json","r") as file:
        coords = json.load(file)
    refatchedData = getWrongSquares(coords,coordsBase)
    areas = fetchAreas(refatchedData)
    
    for name,coord in areas:
        coords[name] = coord

    with open("holeData.json","w") as file:
        json.dump(coords, file, indent=4)


if __name__ == "__main__":
    mapPaths()
    #singleCall()
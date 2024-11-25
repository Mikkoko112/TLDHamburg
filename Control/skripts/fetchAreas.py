#!/usr/bin/env python3
import json
import requests
from math import floor,ceil,dist
from geopy import distance
from time import sleep

modif = 1000

def roundValues(coords:list,modif:int)->list:
   
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
        
        if(name != "13937"):
            holeData[name] = getNotes(roundValues(coords,modif))
            print("{:.2f}% {} {} {}".format(idx/len(relevantAres)*100,name,len(holeData[name]),roundValues(coords,modif)))
            idx+=1
            with open("holeDataSAFE.json","w") as file: #after Run change
                json.dump(holeData, file, indent=4)

        sleep(15)

    return holeData

def getNotes(coordsMinMax:list)->dict:
    body = {"bbox": coordsMinMax}
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf624884e5ad2d208a4ef2abb164f9f203b5b5",
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
                9.9489717,
                53.5462321
            ],
            [
                9.9561542,
                53.5588747
            ]
        ]
   
    areas = getNotes(area)

    with open("holeDataTest.json","w") as file:
        json.dump(areas, file, indent=4)
def mapPaths():
    with open("../data/fetchAreasFullData.json","r") as file:
        coords = json.load(file)

    areas = fetchAreas(coords)
    
    with open("holeData.json","w") as file:
        json.dump(areas, file, indent=4)


    
def correctTheHoleData():
    with open("../data/fetchAreasFullData.json","r") as file:
        coordsBase = json.load(file)

    with open("holeData.json","r") as file:
        coords = json.load(file)
    
    print(len(coords),len(coordsBase),len(coordsBase)-len(coords))

    refatchedData = getWrongSquares(coords,coordsBase)
    areas = fetchAreas(refatchedData)
    
    print(len(refatchedData))

    for name,coord in areas.items():
        coords[name] = coord

    with open("refetchData.json","w") as file:
        json.dump(areas, file, indent=4)


if __name__ == "__main__":
    with open("../optionsfile.json","r") as file:
        options = json.load(file)

    modif = options["modif"]

    #mapPaths()
    #singleCall()
    #correctTheHoleData()
    checkLength()
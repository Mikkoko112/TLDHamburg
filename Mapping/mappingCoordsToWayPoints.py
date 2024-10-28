#!/usr/bin/env python3
import json
import requests
from math import floor,ceil

modif = 100

def findSmalestAndLagestCoord(coords)->list:
    sm,la = [100,100],[0,0]
    for name,coord in coords.items():
        
        for j,c in enumerate(coord):
            for i,ax in enumerate(c):
               
                if ax < sm[i]:
                    sm[i] = ax
                elif ax > la[i]:
                    la[i] = ax
    return [[sm[0],la[1]],[la[0],sm[1]]]

def roundValues(coords:list)->list:
   
    coordsCopy = list(coords)
    func = [floor,ceil]
    for i,c in enumerate(coordsCopy):
        for j,ax in enumerate(c):
            coordsCopy[i][j] = (func[i](ax*modif))/modif 
    return coordsCopy

def getNotes(coordsMinMax:list):
    body = {"bbox": coordsMinMax}
    print(body)
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

#def getPath(startEnd:list):

def getSystematicCalles(coordsMinMax:list):
    for x in range(int(coordsMinMax[0][0]*modif),int(coordsMinMax[1][0]*modif),int(0.01*modif)):
        for y in range(int(coordsMinMax[0][1]*modif),int(coordsMinMax[1][1]*modif),int((-0.01)*modif)):
            #print(x/modif,y/modif)
            pass



def mapPaths():
    searchArea = 0.015
    with open("cleanedCoors.json","r") as file:
        coords = json.load(file)

    for name,setCord in coords.items():
        #requestArea = [
        #    [setCord[1][0]-searchArea,setCord[1][1]+searchArea],
        #    [setCord[1][0]+searchArea,setCord[1][1]-searchArea]
        #]
        requestArea = [[9.82, 53.65], [10.21, 53.54]]
        relevantNotes = getNotes(requestArea)
        print(relevantNotes)

if __name__ == "__main__":
    mapPaths()




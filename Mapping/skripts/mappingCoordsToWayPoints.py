#!/usr/bin/env python3
import json
import requests
from math import floor,ceil,dist
from geopy import distance


modif = 100

def findSmalestAndLagestCoord(coords)->list:
    sm,la = [100,100],[0,0]
    for name,coord in coords:
        for j,c in enumerate(coord):
            for i,ax in enumerate(c):
                if ax != True:    
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

#def getPath(startEnd:list):

def getSystematicCalles(coordsMinMax:list):
    for x in range(int(coordsMinMax[0][0]*modif),int(coordsMinMax[1][0]*modif),int(0.01*modif)):
        for y in range(int(coordsMinMax[0][1]*modif),int(coordsMinMax[1][1]*modif),int((-0.01)*modif)):
            #print(x/modif,y/modif)
            pass

def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km

def getAreaBetweenPoints(NW:list,SO:list)->float:
    height = getDistanceBetweenPoints([NW[1],NW[0]],[SO[1],NW[0]])
    length = getDistanceBetweenPoints([NW[1],NW[0]],[NW[1],SO[0]])
    return height*length

def getCallingAreas(traficLights:dict)->list:
    def isInRange(ent:list,sr:list)->bool:
        minDistance = 1.5
        distance = getDistanceBetweenPoints(ent,sr)

        if distance <= minDistance:
            return True
        
        return False
    def isMarked(ent:list)->bool:
        
        return len(ent)==4

    outPutAreas = {}
    dictLen,ind,ismarked,summarked = len(traficLights),0,0,0
    for name,ent in traficLights.items(): #geht über alle Items
        
        if(not isMarked(ent)): #guckt ob das nächste Item bearbeitet wurde
            coordMinMax,traficLightsPerArea = [],[[name,ent]]
            traficLights[name].append([True])
            ismarked+=1
            for nameSr,sr in traficLights.items():
                if(not isMarked(sr)):
                    if(isInRange(ent[1],sr[1])):
                        traficLightsPerArea.append([nameSr,sr])
                        traficLights[nameSr].append([True])
                        ismarked+=1
            coordMinMax = findSmalestAndLagestCoord(traficLightsPerArea)
            outPutAreas[name] = [coordMinMax,traficLightsPerArea]
            summarked += len(traficLightsPerArea)
            print("{:.2f}% {} {}/{} {}".format(ismarked/dictLen*100
                                     ,len(traficLightsPerArea)
                                     ,summarked,len(traficLights)
                                     ,[[coordMinMax[0][0]<coordMinMax[1][0]],[coordMinMax[0][1]>coordMinMax[1][1]]]))
        ind+=1
    return outPutAreas


def generateAreas():
    searchArea = 0.015
    with open("../data/cleanedCoors.json","r") as file:
        coords = json.load(file)

    areas = getCallingAreas(coords)
    print(len(areas))
    with open("../data/outPutAresSmall.json","w") as file:
        json.dump(areas, file, indent=4)

def fetchAreas(relevantAres:dict):
    holeData = {}
    for name, note in relevantAres.items():
        coords = note[0]
        print(coords)
        #holeData[name] = getNotes(coords)
    
    return holeData


def getSingleNoteInfoTest():
    data = getNotes([[8.681495, 49.41461], [8.686057,49.41943]])

    with open("../data/testData.json","w") as file:
        json.dump(data, file, indent=4)

def mapPaths():
    with open("../data/outPutAres.json","r") as file:
        coords = json.load(file)

    areas = fetchAreas(coords)
    
    with open("holeData.json","w") as file:
        json.dump(areas, file, indent=4)

if __name__ == "__main__":
    generateAreas()
    #mapPaths()
    #print(getDistanceBetweenPoints([],[]))
    #print(getAreaBetweenPoints([9.82, 53.65], [9.82, 53.65]))




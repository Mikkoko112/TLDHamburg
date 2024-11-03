#!/usr/bin/env python3
import json
import requests
from math import floor,ceil,dist
from geopy import distance

def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km


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
    return [[sm[0],sm[1]],[la[0],la[1]]]

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
                                     ,[[coordMinMax[0][0]<coordMinMax[1][0]],[coordMinMax[0][1]<coordMinMax[1][1]]]))
        ind+=1
    return outPutAreas



def generateAreas():

    with open("../data/cleanedCoorsMin.json","r") as file:
        coords = json.load(file)

    areas = getCallingAreas(coords)
    print(len(areas))
    with open("../data/outPutAreasSmallMin.json","w") as file:
        json.dump(areas, file, indent=4)

if __name__ == "__main__":
    generateAreas() 
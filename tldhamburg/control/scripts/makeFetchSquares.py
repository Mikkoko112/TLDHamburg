#!/usr/bin/env python3
import json
import requests
from math import floor,ceil,sqrt
from geopy import distance
import sys

searchTraffic,searchArea = 0.01,1.5


nameOfProcessedThing,nameOfOutputfile="../data/cleanedCoorsAverage.json","../data/fetchAreasFullDataRerun.json"
'''

'''
def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km


def findSmallestAndLargestCoord(coords)->list:
    sm,la = [100,100],[0,0]
    for name,coord in coords:
        for j,c in enumerate(coord):
            for i,ax in enumerate(c):
                if ax != True:    
                    if ax < sm[i]:
                        sm[i] = ax
                    if ax > la[i]:
                        la[i] = ax
    return [[sm[0],sm[1]],[la[0],la[1]]]

def getCallingAreas(trafficLights:dict)->list:
    def isInRange(ent:list,sr:list)->bool:
        minDistance = searchTraffic if len(sys.argv) > 1 and sys.argv[1] == "1" else searchArea
        
        distance = getDistanceBetweenPoints(ent,sr)

        if distance <= minDistance:
            return True
        
        return False
    def isMarked(ent:list)->bool:
        
        return len(ent)==4

    outPutAreas = {}
    dictLen,ind,ismarked,summarked = len(trafficLights),0,0,0
    print(len(trafficLights))
    for name,ent in trafficLights.items(): #geht ueber alle Items
        
        if(not isMarked(ent)): #guckt ob das naechste Item bearbeitet wurde
            coordMinMax,trafficLightsPerArea = [],[[name,ent]]
            trafficLights[name].append([True])
            ismarked+=1
            for nameSr,sr in trafficLights.items():
                if(not isMarked(sr)):
                    if(isInRange(ent[1],sr[1])):
                        trafficLightsPerArea.append([nameSr,sr])
                        trafficLights[nameSr].append([True])
                        ismarked+=1
            coordMinMax = findSmallestAndLargestCoord(trafficLightsPerArea)
            outPutAreas[name] = [coordMinMax,trafficLightsPerArea]
            summarked += len(trafficLightsPerArea)
            
            print("{:.2f}% {} {}/{} {}".format(ismarked/dictLen*100
                                     ,len(trafficLightsPerArea)
                                     ,summarked,len(trafficLights)
                                     ,[[coordMinMax[0][0]<coordMinMax[1][0]],[coordMinMax[0][1]<coordMinMax[1][1]]]))
        ind+=1
    return outPutAreas



def generateAreas():

    with open("../data/cleanedCoorsAverage.json","r") as file:
        coords = json.load(file)
    print("minDistance ist:{}".format( searchTraffic if len(sys.argv) > 1 and sys.argv[1] == "1" else searchArea))
    areas = getCallingAreas(coords)
    print(len(areas))
    with open(nameOfOutputfile,"w") as file:
        json.dump(areas, file, indent=4)

if __name__ == "__main__":
    generateAreas() 
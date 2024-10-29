#!/usr/bin/env python3
import json
from geopy import distance




def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km

def closestCordToMid(ent:list,srList:list):
    minDist,minCoord = 1,[100,100]
    zminDist,zminCoord = 1.5,[100,100]
    
    for cord in srList:
        dist = getDistanceBetweenPoints(ent,cord)
        if dist < zminDist:
            if dist < minDist:
                zminDist = minDist
                zminCoord = minCoord
                minDist = dist
                minCoord = cord
            else:
                zminDist = dist
                zminCoord = cord
    return minCoord
def calcMean(coords:list)->list:
    xmean,ymean = 0,0
    for item in coords:
        xmean += item[0]
        ymean += item[1]
    xmean /= len(coords)
    ymean /= len(coords)

    return [xmean,ymean]

with open("../data/thingsLoc.json","r") as file:
    dataLanes = json.load(file)

midCoords = {}

for n,lanes in enumerate(dataLanes):
    #print(lanes)
    sumCords = [
        [0,0],
        [0,0]
    ]
    if True:
        ingress,path,exgress = list(),list(),list()
        
        if len(dataLanes[lanes]) < 2: break

        meanPath = calcMean(dataLanes[lanes][1])
        for i,paths in enumerate(dataLanes[lanes]):
            
            #if i == 0: ingress = calcMean(paths)
            #if i == 2: exgress = calcMean(paths)

            if i == 0: ingress = closestCordToMid(meanPath,paths) #evtl hier nächste Coordinate zu mean path
            if i == 1: path = meanPath
            if i == 2: exgress = closestCordToMid(meanPath,paths) #.||.
        midCoords[lanes] = [ingress,path,exgress]

with open("../data/cleanedCoorsMin.json","w") as jsonFile:
    json.dump(midCoords,jsonFile,indent=4)


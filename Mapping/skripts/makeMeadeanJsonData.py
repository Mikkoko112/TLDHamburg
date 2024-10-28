#!/usr/bin/env python3
import json


def calcMean(coords:list)->list:
    xmean,ymean = 0,0
    for item in coords:
        xmean += item[0]
        ymean += item[1]
    xmean /= len(coords)
    ymean /= len(coords)

    return [xmean,ymean]

with open("./thingsLoc.json","r") as file:
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
        for i,paths in enumerate(dataLanes[lanes]):
            
            if i == 0: ingress = calcMean(paths) #evtl hier nächste Coordinate zu mean path
            if i == 1: path = calcMean(paths)
            if i == 2: exgress = calcMean(paths) #.||.
        midCoords[lanes] = [ingress,path,exgress]

with open("./cleanedCoors.json","w") as jsonFile:
    json.dump(midCoords,jsonFile,indent=4)


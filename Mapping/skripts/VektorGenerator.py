#!/usr/bin/env python3
import json
from makeFetchSquares import findSmalestAndLagestCoord,getDistanceBetweenPoints
from math import acos,cos,sqrt

def findFurthestAndNearesCoord(mainCoord:list,coordList:list):
    nearest,furthest = list(),list()
    minDist,maxDist = 100,0
    for coord in coordList:
        print(mainCoord,coord)
        dist = getDistanceBetweenPoints(mainCoord,coord)
        if dist < minDist:
            minDist = dist
            nearest = coord
        if dist > maxDist:
            maxDist = dist
            furthest = coord
    return (nearest,furthest)

def generateVektor(mainCoord:list,coordList:list): #Vektor zeigt zum point!
    minCo,maxCo = findFurthestAndNearesCoord(mainCoord,coordList)
    vec = [minCo[0]-maxCo[0],minCo[1]-maxCo[1]]
    return vec

def getZentroid(coordList:list)->list:
    xmean,ymean = 0,0
    for item in coordList:
        xmean += item[0]
        ymean += item[1]
    xmean /= len(coordList)
    ymean /= len(coordList)

    return [xmean,ymean]


def getDegree(vec:list)->float:
    standartVec = [0,1]
    dot = sum([0*vec[0],1*vec[1]])
    lengthVec = sqrt(vec[0]**2+vec[1]**2)
    return acos(dot/lengthVec)

def genPerPrimarySignal(coords)->dict:
    out = dict()
    for name,coords in coords.items():
        if len(coords) > 1:
            meanCoord = getZentroid(coords[1])
            vec0,vec2 = list(),list()
            if len(coords[0]) != 0:
                vec0 = generateVektor(meanCoord,coords[0])
                vec0.append(getDegree(vec0))
            if len(coords) > 2:
                vec2 = generateVektor(meanCoord,coords[2])
                vec2.append(getDegree(vec2))
            out[name] = [vec0,meanCoord,vec2]
    return out

def startGenerator()->None:
    with open("../data/thingsLoc.json","r") as file:
        coords = json.load(file)

    vektorData = genPerPrimarySignal(coords)
    
    with open("../data/vectorisation.json","w") as file:
        json.dump(vektorData, file, indent=4)

if __name__ == "__main__":
    startGenerator()


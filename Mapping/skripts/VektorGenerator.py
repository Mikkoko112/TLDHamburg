#!/usr/bin/env python3
import json
from makeFetchSquares import findSmalestAndLagestCoord,getDistanceBetweenPoints
from math import acos,cos,sqrt
import sys
if len(sys.argv) > 1: #this can maybe be changed to options
    nameOfThingsLocation = sys.argv[1]
else:
    nameOfThingsLocation = "../data/thingsLoc.json"

if len(sys.argv) > 2:
    nameOfOutputfile = sys.argv[2]
else:
    nameOfOutputfile = "../data/vectorisation.json"
'''
nameOfThingsLocation <- This needs to be set to your ThingsLocation,
                        Default = "../data/thingsLoc.json"
                        Can be set with your 1. arguement
                        
                        This should maybe be changed in code the processes Thingsdata
                        to reduce the points in which the things location lists 
                        are reduced to a single point.
nameOfPutputfile     <- This needs tp be set to your outputfile name
                        Default = "../data/vectorisation
                        Can be set with your 2. arguement



output:json ->          This returns a things json file that contain 
'''

def findFurthestAndNearesCoord(mainCoord:list,coordList:list):
    '''
    mainCoord:list <- This is the first item in coordinates. ent is the primary stationary Element
    coordList: list <- This is the second item in lists of coordiantes. stList contain the differend the street element 
    
    This function does not exclue that a coord is a minimal and maximal distance. This is important.

    return:list -> this returns the coordinate that is the minimal and maximal distance from the mainCoord 
    '''
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
    '''
    mainCoord:list <- This is the main coord one wants to use the vektor as 
    coordList:list <- This is the list of coords one wants to translate into a vector

    The point is computed in to differend ways. The active version now is the mean value of the Path
    The nearest point version can be activated but is not recommendet. This will results in points
    that lay directly beside the zentroid and dicretion information is lost.

    return:list    -> This returns a vector pointing form the computed point to the mainCoord
    '''
    #minCo,maxCo = findFurthestAndNearesCoord(mainCoord,coordList)
    meanCo = getZentroid(coordList)
    vec = [mainCoord[0]-meanCo[0],mainCoord[1]-meanCo[1]] #hier wird es jetzt auf das Centroid focosiert
    #hier könnte noch der vektor normiert werden.

    return vec

def getZentroid(coordList:list)->list:
    '''
    This is dublicate and will be removed soon in place of an univeral comutation file
    '''
    xmean,ymean = 0,0
    for item in coordList:
        xmean += item[0]
        ymean += item[1]
    xmean /= len(coordList)
    ymean /= len(coordList)

    return [xmean,ymean]


def getDegree(vec:list)->float:
    '''
    vec:list <- This is a vector calculated in the generateVektor methode

    We use a standart vector here and not the angle between the ingress and exgress to
    provent dublicate degrees. 

    return:float -> This will return the angle to the standart vector
    '''
    standartVec = [0,1]
    dot = sum([0*vec[0],1*vec[1]])
    lengthVec = sqrt(vec[0]**2+vec[1]**2)
    return acos(dot/lengthVec)

def genPerPrimarySignal(coords:dict)->dict:
    '''
    coords:dict <- This is the dict with the things data

    return:dict -> A dict with every primary signal with its dedicated vector and degree
                   of ingress and exgress lane. The point in the middel is the mean Value
    '''

    out = dict()
    for name,coords in coords.items():
        if len(coords) > 1:
            meanCoord = getZentroid(coords[1])  #this is maybe redundant
            vec0,vec2 = list(),list()
            if len(coords[0]) != 0:
                vec0 = generateVektor(meanCoord,coords[0])
                vec0.append(getDegree(vec0))
            if len(coords) > 2:
                vec2 = generateVektor(meanCoord,coords[2])
                vec2 = [-x for x in vec2]
                vec2.append(getDegree(vec2))
            out[name] = [vec0,meanCoord,vec2]
    return out

def startGenerator()->None:
    with open(nameOfThingsLocation,"r") as file:
        coords = json.load(file)

    vektorData = genPerPrimarySignal(coords)
    
    with open("../data/vectorisation.json","w") as file:
        json.dump(vektorData, file, indent=4)

if __name__ == "__main__":
    startGenerator()


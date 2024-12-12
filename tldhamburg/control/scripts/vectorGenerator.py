#!/usr/bin/env python3
import json
from makeFetchSquares import findSmallestAndLargestCoord,getDistanceBetweenPoints
from math import acos,cos,sqrt,pi,degrees
import sys
if len(sys.argv) > 1: #this can maybe be changed to options
    nameOfThingsLocation = sys.argv[1]
else:
    nameOfThingsLocation = "../data/thingsLoc.json"

if len(sys.argv) > 2:
    nameOfOutputfile = sys.argv[2]
else:
    nameOfOutputfile = "../data/vectorization.json"
'''
nameOfThingsLocation <- This needs to be set to your ThingsLocation,
                        Default = "../data/thingsLoc.json"
                        Can be set with your 1. argument
                        
                        This should maybe be changed in code the processes Thingsdata
                        to reduce the points in which the things location lists 
                        are reduced to a single point.
nameOfPutputfile     <- This needs tp be set to your outputfile name
                        Default = "../data/vectorization
                        Can be set with your 2. argument



output:json ->          This returns a things json file that contain 
'''

def findFurthestAndNearestCoord(mainCoord:list,coordList:list):
    '''
    mainCoord:list <- This is the first item in coordinates. ent is the primary stationary Element
    coordList: list <- This is the second item in lists of coordinates. stList contain the different the street element 
    
    This function does not exclude that a coord is a minimal and maximal distance. This is important.

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

def generateVector(mainCoord:list,coordList:list): #Vektor zeigt zum point!
    '''
    mainCoord:list <- This is the main coord one wants to use the vector as 
    coordList:list <- This is the list of coords one wants to translate into a vector

    The point is computed in to different ways. The active version now is the mean value of the Path
    The nearest point version can be activated but is not recommended. This will results in points
    that lay directly beside the centroid and discretion information is lost.

    return:list    -> This returns a vector pointing form the computed point to the mainCoord
    '''
    #minCo,maxCo = findFurthestAndNearestCoord(mainCoord,coordList)
    meanCo = getCentroid(coordList)
    vec = [mainCoord[0]-meanCo[0],mainCoord[1]-meanCo[1]] #hier wird es jetzt auf das Centroid focosiert
    scaleVec = sqrt(vec[0]**2+vec[1]**2)
    if scaleVec == 0:
        scaleVec = 1
    vec = [vec[0]/scaleVec,vec[1]/scaleVec]
    #hier könnte noch der vektor normiert werden.

    return vec

def getCentroid(coordList:list)->list:
    '''
    This is duplicate and will be removed soon in place of an universal commutation file
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
    vec:list <- This is a vector calculated in the generateVector method

    We use a standard vector here and not the angle between the ingress and egress to
    prevent duplicate degrees. 

    return:float -> This will return the angle to the standard vector
    '''
    def dotProd (vec0,vec1):
        return sum(v0*v1 for v0,v1 in zip(vec0,vec1))

    def crossProd(vec0,vec1):
        assert (len(vec0) == 2) and (len(vec1)==2)
        return vec0[0]*vec1[1] - vec0[1]*vec1[0]
    standardVec = [0,1]
    dot = dotProd(standardVec,vec)

    lengthVec = sqrt(dotProd(vec,vec)) #should be 1
    lengthStd = sqrt(dotProd(standardVec,standardVec)) #this too
    if crossProd(vec,standardVec) < 0:
        return 2*pi-acos(dot/lengthVec)
   
    return acos(dot/lengthVec) 


def genPerPrimarySignal(coords:dict,conjunctionDict:dict)->dict:
    '''
    coords:dict <- This is the dict with the things data

    return:dict -> A dict with every primary signal with its dedicated vector and degree
                   of ingress and egress lane. The point in the middle is the mean Value
    '''

    out = dict()
    for name,coords in coords.items():
        for conjName,body in conjunctionDict.items():
            
            if (name in body["trafficLights"] 
                    and len(body["junctionNodes"]) > 0):
                            #this asserts that the necessary data is present 
                
                meanCoordCalc = getCentroid(coords[1])
                
                print(name,body["junctionNodes"])
                imNodes = body["junctionNodes"]
                meanCoord = findFurthestAndNearestCoord(meanCoordCalc,imNodes)[0]
                
                vec0,vec2 = list(),list()
                if len(coords[0]) != 0:
                    vec0 = generateVector(meanCoordCalc,coords[0])
                    deg = getDegree(vec0)
                    vec0.append(deg)
                    vec0.append(degrees(deg))
                if len(coords) > 2:
                    vec2 = generateVector(meanCoordCalc,coords[2])
                    deg = getDegree(vec2)
                    vec2.append(deg)
                    vec2.append(degrees(deg))
                out[name] = [vec0,meanCoord,vec2]
    return out

def startGenerator()->None:
    with open(nameOfThingsLocation,"r") as file:
        coords = json.load(file)

    with open("../data/conjunctionDict.json","r") as file: 
        conjDict = json.load(file)

    vectorData = genPerPrimarySignal(coords,conjDict)
    
    with open("../data/vectorizationOnMeanPoint.json","w") as file:
        json.dump(vectorData, file, indent=4)

if __name__ == "__main__":
    startGenerator()


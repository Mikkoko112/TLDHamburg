#!/usr/bin/env python3
import json
from geopy import distance




def getDistanceBetweenPoints(ent:list,sr:list)->float:
    '''
    ent:list <- This is the first item in coordinates. ent is the primary stationary Element
    sr: list <- This is the second item in coordinates. st is the street element 
    
    return:float -> This returns the distance in km
    '''
    return distance.distance(ent,sr).km

def closestCordToMid(ent:list,srList:list)->list:
    '''
    ent:list <- This is the first item in coordinates. ent is the primary stationary Element
    srList: list <- This is the second item in lists of coordinates. stList contain the different the street element 
    
    return:list -> this returns the coordinate that is the minimal distance 
    '''
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
    '''
    coords:list <- This is a list of coordinates.
    
    return:list -> This returns the mean element
    '''
    xmean,ymean = 0,0
    for item in coords:
        xmean += item[0]
        ymean += item[1]
    xmean /= len(coords)
    ymean /= len(coords)

    return [xmean,ymean]

def run():
    '''
    This goes over every Element of the File provided and returns it with reduced lists.

    There are two procedures to choose from. 
    -Mean value for ingress, egress
    -Nearest coord to mean value
    This can be changed in code by commenting in and out of the procedures
    '''
    with open("../data/thingsLoc.json","r") as file:
        dataLanes = json.load(file)

    print(dataLanes)

    print(len(dataLanes.keys()))
    midCoords = {}

    j = 0

    for name,lane in dataLanes.items():
        print(name)
        sumCords = [
            [0,0],
            [0,0]
        ]
        j+=1
        ingress,path,egress = list(),list(),list()
        
        if len(lane) < 2: continue

        meanPath = calcMean(lane[1])
        for i,paths in enumerate(lane):
            
            if i == 0: ingress = calcMean(paths)
            if i == 2: egress  = calcMean(paths)

            #if i == 0: ingress = closestCordToMid(meanPath,paths) #evtl hier nächste Coordinate zu mean path
            if i == 1: path = meanPath
            #if i == 2: egress = closestCordToMid(meanPath,paths) #.||.
        midCoords[name] = [ingress,path,egress]

    print(len(midCoords))
    with open("../data/cleanedCoorsAverage.json","w") as jsonFile:
        json.dump(midCoords,jsonFile,indent=4)

if __name__ == "__main__":
    run()
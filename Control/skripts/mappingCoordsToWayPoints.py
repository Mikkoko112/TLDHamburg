#!/usr/bin/env python3
import json
import requests
from math import floor,ceil,dist
from geopy import distance

#this is opselit. This was the first test of direct mapping


modif = 1000

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


def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km

def getAreaBetweenPoints(NW:list,SO:list)->float:
    height = getDistanceBetweenPoints([NW[1],NW[0]],[SO[1],NW[0]])
    length = getDistanceBetweenPoints([NW[1],NW[0]],[NW[1],SO[0]])
    return height*length


def mapCoordsToArea(lightsInArea,areaCords):
    notePoints = areaCords["nodes"]
    lightDict = dict()
    for i,points in enumerate(lightsInArea):
        name = points[0]
        #print(name,points[1][:3])
        print("{:.2f}".format(i/len(lightsInArea)*100))
        pointIds = ["0","0","0"]
        for j,point in enumerate(points[1][1:3]):
            
            for node in areaCords["nodes"]:
                if getDistanceBetweenPoints(node["location"][::-1]
                                           ,point[::-1]) <= 0.01:
                    pointIds[j] = "{}".format(node["nodeId"])
                    print("hit")
                    break
        lightDict[name] = pointIds
    return lightDict
            
def getSingleNoteInfoTest():
    coord = [
            [
                9.947890533333332,
                53.559770762499994
            ],
            [
                9.956933744444443,
                53.54600926249999
            ]
        ]
    changedPos = [[coord[0][0],coord[1][1]],[coord[1][0],coord[0][1]]]
    data = getNotes(roundValues(changedPos))

    with open("../data/testData.json","w") as file:
        json.dump(data, file, indent=4)



def testMapping():
    with open("../data/outPutAresSmall.json","r") as file:
        coords = json.load(file)
    with open("../data/testData.json","r") as file:
        testData = json.load(file)
    
    mapCo = mapCoordsToArea(coords["23229"][1],testData)

    with open("../data/mappingTest.json","w") as file:
        json.dump(mapCo, file, indent=4)

if __name__ == "__main__":
    
    testMapping()




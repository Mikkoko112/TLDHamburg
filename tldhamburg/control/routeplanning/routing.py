#!/usr/bin/env Python3
import requests
import json
import igraph
from math import sqrt,acos,inf,degrees,pi
from tldhamburg.control.routeplanning.fetchRoutes import getRouteFromGraph
modif = 1000
testName = "16963"

def inbound(bound,coord:list)->bool: #vllt schneller, wenn Gegensatzt getestet
    assert (len(bound) == 2 and len(coord) == 2 
                            and all([len(b) == 2 for b in bound]))
    

    xMin = min(bound[0][0], bound[1][0]) 
    xMax = max(bound[0][0], bound[1][0])
    yMin = min(bound[0][1], bound[1][1])
    yMax = max(bound[0][1], bound[1][1])


    return xMin <= coord[0] <= xMax and yMin <= coord[1] <= yMax

def getNearestNode(mainNode:list,nodeList:list)->list:
    nearestDist  = inf
    nearestNode = []
    for node in nodeList:
        dist = sqrt((node[0]-mainNode[0]**2 )+(node[1]-mainNode[1]**2 ))
        if dist < nearestDist:
            nearestDist = dist
            nearestNode = node
    
    return nearestNode

def sortNodeToConjunction(pureRoute:list,conjunctionDict)->dict:
    out = {}
    for i,wayPoint in enumerate(pureRoute):
        for name,data in conjunctionDict.items():
            if inbound(data['bound'],wayPoint):
                
            
                if not name in out:
                    out[name] = []

                out[name].append([i,wayPoint])
    return out

def generateVectorPoint(pointOut:list,pointIn:list): #Vektor zeigt zum point!
    vec = [pointIn[0]-pointOut[0],pointIn[1]-pointOut[1]]
    scaleVec = sqrt(vec[0]**2+vec[1]**2)
    if scaleVec == 0:
        scaleVec = 1
    return [vec[0]/scaleVec,vec[1]/scaleVec]

def getCentroid(coordList:list)->list:
    xmean,ymean = 0,0
    for item in coordList:
        xmean += item[0]
        ymean += item[1]
    xmean /= len(coordList)
    ymean /= len(coordList)

    return [xmean,ymean]

def getDegree(vec:list)->float:
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


def inDegreeOffset(inputDegree, offsetDegree):
    def angleDifference(theta1, theta2):
        """
        Berechnet den kürzesten Abstand (zyklisch) zwischen zwei Winkeln in Grad.
        """
        diff = (theta2 - theta1) % 360
        
        return min(diff, 360 - diff)
    

    #this needs to be fixed. It does not account to the overflow of an angle
    lowerValue,upperValue = offsetDegree-60,offsetDegree+60 #das ist ein offset von 25°
    
    theta = inputDegree % 360
    theta1 = lowerValue % 360
    theta2 = upperValue % 360

    # Falls theta1 > theta2, über den 0-Punkt hinweg prüfen
    inBetween = False
    if theta1 > theta2:
        inBetween = theta >= theta1 or theta <= theta2
    else:
        inBetween = theta1 <= theta <= theta2
    
    #something stinks here. This needs to be fixed look at 16963
    dist_to_theta1 = abs(angleDifference(theta, offsetDegree))
    dist_to_theta2 = abs(angleDifference(theta, offsetDegree))
    max_distance = max(dist_to_theta1, dist_to_theta2)

    return inBetween, max_distance
    

def roundValues(value:float)->list: #bad naming in relation to other functions
    return (round(value*modif)/modif)

def lanesOverlap(primarydegIn,primarydegOut,inDeg,outDeg)->bool:
    return [inDegreeOffset(roundValues(inDeg) ,primarydegIn ),
            inDegreeOffset(roundValues(outDeg),primarydegOut)]

def getBestPrimarySignal(possibleSignals,conjId:str="0")->str:
    smallestError = 0
    outPrimarySignal = ""
    
    
    for i,item in enumerate(possibleSignals):
        
        values = item[1]+item[2]
        if conjId == testName:
            print(item[0],values)
        if values > smallestError:
            outPrimarySignal = item[0]
            smallestError = values
    
    if conjId == testName:
        print(outPrimarySignal,smallestError)

    return outPrimarySignal

def getRouteTrafficLights(route:list, conjFile:dict,conjList:list,vectorization:dict)->dict:
    trafficLights,debugVector = dict(),[]
    for name,data in conjList.items():
        pointList    = [dat[1] for dat in data]
        pointIndex   = [dat[0] for dat in data]
        allPossiblePrimarysignal = []
        for primarySignalName in conjFile[name]['traficLights']:
            
            meanofPoints =  vectorization[primarySignalName][1]

            vecIn  = generateVectorPoint(meanofPoints,route[pointIndex[ 0]-1]) 
            vecOut = generateVectorPoint(meanofPoints,route[pointIndex[-1]+1]) 

            degIn  = degrees(getDegree(vecIn))
            degOut = degrees(getDegree(vecOut))

            primarydegIn  = vectorization[primarySignalName][0][3]
            primarydegOut = vectorization[primarySignalName][2][3]


            # # #please change this back at a later stage
            # primarydegIn  = vectorization[primarySignalName][2][3]
            # primarydegOut = vectorization[primarySignalName][0][3]

            

            check = lanesOverlap(primarydegIn,primarydegOut,degIn,degOut)
                        
            if name == testName:
                print(primarySignalName)
                print("Incoord",route[pointIndex[ 0]-1])
                print("Outcoord",route[pointIndex[-1]+1])
                print("vectors",vecIn,vecOut)
                print("degrees",degIn,degOut)
                print("primary degrees",primarydegIn,primarydegOut)

            if all([tr[0] for tr in check]):

                
    

                allPossiblePrimarysignal.append([primarySignalName,
                                                check[0][1],
                                                check[1][1]])
                #break
        if len(allPossiblePrimarysignal) > 0:
            trafficLights[name] = getBestPrimarySignal(allPossiblePrimarysignal,name)
                
    return trafficLights

def generateGeoJsonData(trafficLights:dict,conjList:dict)->dict:
    def getPointData(conjNodes:list)->list: #needs Change
        return conjNodes[0]

    out = {
        "type":"FeatureCollection",
    }
    features = []
    i=1
    for conj,traffic in trafficLights.items():
        element =         {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": getPointData(conjList[conj])[1]
            },
            "properties": {
                "id": "{}".format(conj),
                "object": "primary_signal",
                "way-point": getPointData(conjList[conj])[0]
            }
        }
        features.append(element)

        i+=1
    out["features"] = features
    return out

def purifyRoute(route:dict,index:int=0)->list:
    return list(route['features'][index]['geometry']['coordinates'])

def getTrafficLightsRoute(routeList:dict,test:bool=True)->dict:
    with open("tldhamburg/control/data/conjunctionDict.json","r") as file:
        conjDict = json.load(file)
    
    with open("tldhamburg/control/data/vectorizationOnMeanPointInvert.json","r") as file:
        vectorization = json.load(file)

    for i in range(len(routeList['features'])):
        pureRoute = purifyRoute(routeList,index=i)
        
        conjList = sortNodeToConjunction(pureRoute,conjDict)
        trafficLightsList = getRouteTrafficLights(pureRoute,conjDict,conjList,vectorization)
        if test:
            dic = {"wayPoints":pureRoute,
           "conjList":conjList,
           "trafficLights":trafficLightsList}
            with open("tldhamburg/control/maps/mappingTest.json","w") as file:
                json.dump(dic,file,indent=4)
            exit(1)
        jsonData = generateGeoJsonData(trafficLightsList,conjList)
        
        routeList["features"][i]["properties"]["trafficlights"] = jsonData
        
    return routeList


def test():
    with open("../data/conjunctionDict.json","r") as file:
        conj = json.load(file)
    
    with open("../data/vectorizationOnMeanPoint.json","r") as file:
        vectorization = json.load(file)

    graph = igraph.load("../data/shHamburg.gml")
    #testRoute1
    routeHole = getRouteFromGraph([[9.946091651916504,53.59207534790039 ],
                                [10.0772705078125,53.61192321777344]],graph)
   # testRoute2,gen popenbüttel
    # routeHole = getRouteFromGraph([[10.015552520751953,53.64086151123047 ], 
    #                             [10.075848579406738,53.65281677246094]],graph)
    #ohlsdorf route
    # routeHole = getRouteFromGraph([[10.059387,53.6235983 ], #ohlsdorf
    #                              [10.061087,53.624418]],graph)
    
    pureRoute = purifyRoute(routeHole)
    conjList = sortNodeToConjunction(pureRoute,conj)
    trafficLightsList = getRouteTrafficLights(pureRoute,conj,conjList,vectorization)
    
    dic = {"wayPoints":pureRoute,
           "conjList":conjList,
           "trafficLights":trafficLightsList}
    with open("ohlsdorfRoute.json","w") as file:
        json.dump(dic,file,indent=4)

if __name__ == "__main__":
    test()
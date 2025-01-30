#!/usr/bin/env Python3
'''
This module is used to map the primary signals to the respective routes.
The main function is "getTrafficLightsRoute".

This modules relies heavily on the presents of the generated data and will
not work if there is any corrupted data.  

Author: Helge Rasmus Steen

'''


import requests
import json
import time
import igraph
from math import sqrt,acos,inf,degrees,pi
from tldhamburg.control.routeplanning.fetchRoutes import getRouteFromGraph
modif = 1000
testName = "6585"

def inbound(bound,coord:list)->bool: #vllt schneller, wenn Gegensatzt getestet
    '''
    Input
        <- bound = [[...],[...]] This is the bounding box one wants to check for.
        <- coord = [...,...] This is the coord one wants to check for.
    
    Output
        -> inBound = ... The output is a bool that is true if the coord is in
                            the bounding box and false if its is not.


    The order of [lat,log] is not relevant as long as the bound and the 
    coord adhere to the same order. 
    '''


    assert (len(bound) == 2 and len(coord) == 2 
                            and all([len(b) == 2 for b in bound]))
    

    xMin = min(bound[0][0], bound[1][0]) 
    xMax = max(bound[0][0], bound[1][0])
    yMin = min(bound[0][1], bound[1][1])
    yMax = max(bound[0][1], bound[1][1])


    return xMin <= coord[0] <= xMax and yMin <= coord[1] <= yMax

def getNearestNode(mainNode:list,nodeList:list)->list:
    '''
    Input
        <- mainNode = [...,...] This is the main node to check for distance
        <- nodeLust = [[...,...],...] This is the node list to check through
    
    Output 
        -> nearestNode = [...,...] This is the nearest node tho the main node
                                    If the main node is in the list, it will
                                    return the main node.

    This function uses the euclidean norm. This assumption is made to reduce
    calculation time. The euclidean norm work in this subspace of the non 
    euclidean world because we only look at the relative spaces in hamburg.
    This projection to a euclidean norm can be seen as the projection of a
    submanifold. 
    '''
    nearestDist  = inf
    nearestNode = []
    for node in nodeList:
        dist = sqrt(((node[0]-mainNode[0])**2 )+((node[1]-mainNode[1])**2 ))
        if dist < nearestDist:
            nearestDist = dist
            nearestNode = node
    
    return nearestNode

def sortNodeToConjunction(pureRoute:list,conjunctionDict)->dict:
    '''
    Input
        <- pureRoute = [[...,...],...] This is the route represented as a list
                                        of coordinates. It is in chronological 
                                        Order.
        <- conjunctionDict = {}        This is the conjunction dict. It contains
                                        the bounding box of every conjunction.
    Output
        -> out = {
                conjunctionName: [
                    [int, [...,...]],
                    ...
                ]
            } The output is a dict keys for every hit conjunction. It contains
                a list with every coordinate and index of this coordinate in the
                route.
    '''
    out = {}
    for i,wayPoint in enumerate(pureRoute):
        for name,data in conjunctionDict.items():
            if inbound(data['bound'],wayPoint):
                
            
                if not name in out:
                    out[name] = []

                out[name].append([i,wayPoint])
    return out

def generateVectorPoint(pointOut:list,pointIn:list): #Vektor zeigt zum point!
    '''
    Input
        <- pointOut = [...,...] This is the point outside of the conjunction
        <- pointIn  = [...,...] This is the point inside  of the conjunction
    
    Output
        -> vector   = [...,...] This is the vector from outside in.

    This vector points from the outside of the conjunction inside and 
    is normed.
    '''
    vec = [pointIn[0]-pointOut[0],pointIn[1]-pointOut[1]]
    scaleVec = sqrt(vec[0]**2+vec[1]**2)
    if scaleVec == 0:
        scaleVec = 1
    return [vec[0]/scaleVec,vec[1]/scaleVec]

def getCentroid(coordList:list)->list:
    '''
    Input
        <- coordList = [[...,...],...] This is the list of coords that is averaged

    Output
        -> centroid  = [...,...]        This is the mean coordinate generated
    
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
    Input
        <- vec = [...,...]      This is a vector. I can have more then 2 elements.
                                This function only uses the first two indices.

    Output
        -> degree = ...         This is the degree between vec and the standard
                                vector [0,1] in radians.
    
    
    This function uses the cross product to allow the full radius span.
    Otherwise the degree is not rotation affine and is caped between 
    [0,pi].
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


def inDegreeOffset(inputDegree, offsetDegree):
    '''
    Input
        <- inputDegree = ...    This is the degree of the route to the standard
                                vector. It was calculated in getDegree.
                                The input should be in degree.
        <- offesetDegree = ...  This is the degree of the primary signal
                                from the primary signal
    
    Output
        -> inBetween   = ...   This is a bool that states if the inputDegree
                                is in the interval of the offsetDegree

        -> max_distance = ...  This is the distance between the inputDegree 
                                and offsetDegree.

    The offset is set to 65° to grantee that the hit of a primary signal. 
    The evaluation of the minimal error selects the right direction. 
                                
    '''



    def angleDifference(theta1, theta2):
        """
        Calcualtes the distance between two angles
        """
        diff = (theta2 - theta1) % 360
        
        return min(diff, 360 - diff)
    

    #this needs to be fixed. It does not account to the overflow of an angle
    lowerValue,upperValue = offsetDegree-65,offsetDegree+65 #das ist ein offset von 25°
    
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
    

def roundValues(value:float)->list: 
    '''
    Input
        <- value = ... this is the value that is to be round.

    Output
        -> roundedValue = ... this is the value rounded to the modif-st
                                decimal place

    This function is equivalent to the round(value,modif) function.
    
    '''
    return (round(value*modif)/modif)

def lanesOverlap(primarydegIn,primarydegOut,inDeg,outDeg)->bool:
    '''
    Input
        <- primarydegIn  = ... This is the drive in  degree of the primary signal
        <- primarydegOut = ... This is the drive out degree of the primary signal
        <- inDeg  = ... This is the drive  in degree of the route
        <- outDeg = ... This is the drive out degree of the route 
    
    Output
        -> checkResults = [[bool,float],[bool,float]] This is a list of two
                                                        inDegreeOffset calls.
    
    '''


    return [inDegreeOffset(roundValues(inDeg) ,primarydegIn ),
            inDegreeOffset(roundValues(outDeg),primarydegOut)]

def getBestPrimarySignal(possibleSignals)->str:
    '''
    Input
        <- possibleSignals = [[primarySignalName,
                                 driveInError,
                                driveOutError],
                             ...] These are the results of every primary signals
                                    with the respective errors. 
    Output
        -> outPrimarySignal = ... This is the best primary signal.
    '''
    
    
    smallestError = inf
    outPrimarySignal = ""
    
    
    for i,item in enumerate(possibleSignals):
        
        values = item[1]+item[2]
        if values < smallestError:
            outPrimarySignal = item[0]
            smallestError = values
    

    return outPrimarySignal

def getRouteTrafficLights(route:list, conjFile:dict,conjList:list,vectorization:dict)->dict:
    '''
    Input
        <- route = [...]    This is the pure route with only coordinates
        <- conjFile = {...} This is the conjunction dict file. 
        <- conjList = [...] This is the list of conjunctions with relevant
                            nodes and indices
        <- vectorization = {...} This is the vectorization data.
    
    Output
        -> trafficLights = {...} This is a dict with conjunction names with
                                    the key being the conjunction id and 
                                    the value being the relevant primary signal

    '''
    trafficLights,debugVector = dict(),[]
    #This lists every hit conjunction.
    for name,data in conjList.items():
        pointList    = [dat[1] for dat in data]
        pointIndex   = [dat[0] for dat in data]
        allPossiblePrimarysignal = []
        #Iterates over every possible primary signals in the conjunctions
        for primarySignalName in conjFile[name]['trafficLights']:
            
            meanofPoints =  vectorization[primarySignalName][1]
            try:
                vecIn  = generateVectorPoint(meanofPoints,route[pointIndex[ 0]-1]) 
                vecOut = generateVectorPoint(meanofPoints,route[pointIndex[-1]+1]) 
            except IndexError:
                #This needs to be done to catch the cases in which the traffic 
                #light is directly on the beginning or end of the route
                continue
            degIn  = degrees(getDegree(vecIn))
            degOut = degrees(getDegree(vecOut))

            primarydegIn  = vectorization[primarySignalName][0][3]
            primarydegOut = vectorization[primarySignalName][2][3]


            # # #please change this back at a later stage
            # primarydegIn  = vectorization[primarySignalName][2][3]
            # primarydegOut = vectorization[primarySignalName][0][3]

            

            check = lanesOverlap(primarydegIn,primarydegOut,degIn,degOut)
                    
                    

            if all([tr[0] for tr in check]):

                        
                #if name == testName:
                #    print(primarySignalName)
                #    print("Incoord",route[pointIndex[ 0]-1])
                #    print("Outcoord",route[pointIndex[-1]+1])
                #    print("vectors",vecIn,vecOut)
                #    print("degrees",degIn,degOut)
                #    print("primary degrees",primarydegIn,primarydegOut)
    

                allPossiblePrimarysignal.append([primarySignalName,
                                                check[0][1],
                                                check[1][1]])
                #break
        if len(allPossiblePrimarysignal) > 0:
            trafficLights[name] = getBestPrimarySignal(allPossiblePrimarysignal)
                
    return trafficLights

def generateGeoJsonData(trafficLights:dict,conjList:dict,vectorData:dict)->dict:
    '''
    Input
        <- trafficLights = {...}    This is a dict with conjunctions as keys
                                    and the value being the relevant primary
                                    signal
        <- conjList      = [...]   This is the list of the relevant conjunctions.
        <- vectorData    = {...}   This is the vector data.
    

    Output
        -> primarySignalData = {...} This is the property section of the geojson
                                        file
    '''
    def getPointData(trafficLightPos,conjNodes:list)->list: 
        coordsOfConjunctionNodes  = [node[1] for node in conjNodes]
        nearestRouteNode          = getNearestNode(trafficLightPos,coordsOfConjunctionNodes)
        nearestRouteNodeWithIndex = [node for node in conjNodes 
                                     if node[1] == nearestRouteNode][0]
        return nearestRouteNodeWithIndex

    out = {
        "type":"FeatureCollection",
    }
    features = []
    i=1

    for conj,traffic in trafficLights.items():
        
        conjunctionDataPoint = getPointData(vectorData[traffic][1],conjList[conj])

        element =         {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": conjunctionDataPoint[1]
            },
            "properties": {
                "id": "{}".format(conj),
                "object": "primary_signal",
                "way-point": conjunctionDataPoint[0]
            }
        }
        features.append(element)

        i+=1
    out["features"] = features
    return out

def purifyRoute(route:dict,index:int=0)->list:
    '''
    Input
        <- route = ... This is a dict in GeoJson file that represents the route
        <- Index = ... This is the index of the route one wants the coordinates too

    Output
        -> coordinateRoute = [[...,...],...] This is the list of coordinates 
                                                representing the route.
    
    '''
    return list(route['features'][index]['geometry']['coordinates'])

def getTrafficLightsRoute(routeList:dict,test:bool=False)->dict:
    '''
    Input
        <- routeList = {...} This is the route as a geojson dict.
    
    Output
        -> routeList = {...} This is the route as a geojson dict with primary 
                                signal information.
    
    '''

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
        
        jsonData = generateGeoJsonData(trafficLightsList,conjList,vectorization)
        
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
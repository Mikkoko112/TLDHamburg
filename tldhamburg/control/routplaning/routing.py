#!/usr/bin/env Python3
import requests
import json
import igraph
from math import sqrt,acos,inf,degrees,pi
from fetchRoutes import getRouteFromGraph
modif = 1000

def getRoute(coordsStartEnd:list)->dict:

    body = {"coordinates": coordsStartEnd}
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        "Authorization": "5b3ce3597851110001cf624884e5ad2d208a4ef2abb164f9f203b5b5",
        "Content-Type": "application/json; charset=utf-8",
    }
    call = requests.post(
        "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
        json=body,
        headers=headers,
        timeout=5,
    )

    return json.loads(call.text)
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

def sortNodeToConjuction(pureRoute:list,conjuctionDict)->dict:
    out = {}
    for i,wayPoint in enumerate(pureRoute):
        for name,data in conjuctionDict.items():
            if (name == "22004"):
                print(name,data['bound'],wayPoint)
            if inbound(data['bound'],wayPoint):
                if (name == "22004"):
                    print("hit",wayPoint)
            
                if not name in out:
                    out[name] = []

                out[name].append([i,wayPoint])
                if(name == "22004"):
                    print(out[name])
    return out

def generateVektorPoint(pointOut:list,pointIn:list): #Vektor zeigt zum point!
    vec = [pointIn[0]-pointOut[0],pointIn[1]-pointOut[1]]
    scaleVec = sqrt(vec[0]**2+vec[1]**2)
    if scaleVec == 0:
        scaleVec = 1
    return [vec[0]/scaleVec,vec[1]/scaleVec]

def getZentroid(coordList:list)->list:
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
    standartVec = [0,1]
    dot = dotProd(standartVec,vec)

    lengthVec = sqrt(dotProd(vec,vec)) #should be 1
    lengthStd = sqrt(dotProd(standartVec,standartVec)) #this too
    if crossProd(vec,standartVec) < 0:
        return 2*pi-acos(dot/lengthVec)
   
    return acos(dot/lengthVec) 


def inDegreeOffset(inputDegree, offsetDegree):
    def angleDifference(theta1, theta2):
        """
        Berechnet den kürzesten Abstand (zyklisch) zwischen zwei Winkeln in Grad.
        """
        diff = (theta2 - theta1) % 360
        return min(diff, 360 - diff)
    

    #this needs to be fixed. It does not accound to the overflow of an angle
    #lowerValue,upperValue = offsetDegree-0.6108652,offsetDegree+0.6108652 #das ist ein offset von 45
    lowerValue,upperValue = offsetDegree-70,offsetDegree+70 #das ist ein offset von 25°
    
    theta = inputDegree % 360
    theta1 = lowerValue % 360
    theta2 = upperValue % 360

    # Falls theta1 > theta2, über den 0-Punkt hinweg prüfen
    inBetween = False
    if theta1 > theta2:
        inBetween = theta >= theta1 or theta <= theta2
    else:
        inBetween = theta1 <= theta <= theta2
    

    dist_to_theta1 = angleDifference(theta, theta1)
    dist_to_theta2 = angleDifference(theta, theta2)
    max_distance = max(dist_to_theta1, dist_to_theta2)

    return inBetween, max_distance
    

def roundValues(value:float)->list: #bad naming in relation to other functions
    return (round(value*modif)/modif)

def lanesOverlape(primarydegIn,primarydegOut,inDeg,outDeg)->bool:
    return [inDegreeOffset(roundValues(inDeg) ,primarydegIn ),
            inDegreeOffset(roundValues(outDeg),primarydegOut)]

def getBestPrimarySignal(possibleSignals)->str:
    smallestError = inf
    outPrimarySignal = ""
    for item in possibleSignals:
        values = item[1]+item[2]
        if values < smallestError:
            outPrimarySignal = item[0]

    return outPrimarySignal

def getRouteTraficLights(route:list, conjFile:dict,conjList:list,vectorisation:dict)->dict:
    traficLights,debugVector = dict(),[]
    for name,data in conjList.items():
        pointList    = [dat[1] for dat in data]
        pointIndex   = [dat[0] for dat in data]
        allposiblePrimarysignal = []
        
        for primarySignalName in conjFile[name]['traficLights']:
            
            meanofPoints =  vectorisation[primarySignalName][1]
        #hier muessen noch index fixes gemacht werden, z.b. wenn route endet auf straße
            #print("Before",meanofPoints,route[pointIndex[ 0]-1])
            vecIn  = generateVektorPoint(meanofPoints,route[pointIndex[ 0]-1])
            vecOut = generateVektorPoint(meanofPoints,route[pointIndex[-1]+1])
            #print(vecIn,vecOut)
            degIn  = degrees(getDegree(vecIn))
            degOut = degrees(getDegree(vecOut))
            #print(degIn,degOut)
            primarydegIn  = vectorisation[primarySignalName][0][3]
            primarydegOut = vectorisation[primarySignalName][2][3]

            check = lanesOverlape(primarydegIn,primarydegOut,degIn,degOut)
            if name == "22007":
                print(route)
                
                print()
                print()
                print("vectors",vecIn,vecOut)
                print("degrees",degIn,degOut)
                print("primary degrees",primarydegIn,primarydegOut)
                print("points",route[pointIndex[0]-1:pointIndex[-1]+1])
                print()
                print("pointlist",pointList,pointIndex)
                print()
                print("meanPoint",meanofPoints)
            if all([tr[0] for tr in check]):

                allposiblePrimarysignal.append([primarySignalName,
                                                check[0][1],
                                                check[1][1]])
                #break
        if len(allposiblePrimarysignal) > 0:
            
            traficLights[name] = getBestPrimarySignal(allposiblePrimarysignal)
                
    return traficLights

def generateGeoJsonData(traficLights:dict,conjList:dict)->dict:
    def getPointData(conjNodes:list)->list: #needs Change
        return conjNodes[0]

    out = {
        "type":"FeatureCollection",
    }
    features = []
    i=1
    for conj,trafic in traficLights.items():
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

def pruifyRoute(route:dict,index:int=0)->list:
    return list(route['features'][index]['geometry']['coordinates'])

def getTraficLightsperRoute(routeList:dict)->dict:
    with open("data/conjuctionDict.json","r") as file:
        conjDict = json.load(file)
    
    with open("data/vectorisation.json","r") as file:
        vectorisation = json.load(file)

    for i in range(len(routeList['features'])):
        pureRoute = pruifyRoute(routeList,index=i)
        
        conjList = sortNodeToConjuction(pureRoute,conjDict)
        print(conjList)
        traficLightsList = getRouteTraficLights(pureRoute,conjDict,conjList,vectorisation)
        jsonData = generateGeoJsonData(traficLightsList,conjList)
        routeList["features"][i]["properties"]["traficlights"] = jsonData
        
    return routeList


def test():
    with open("../data/conjuctionDict.json","r") as file:
        conj = json.load(file)
    
    with open("../data/vectorisation.json","r") as file:
        vectorisation = json.load(file)

    graph = igraph.load("../data/shHamburg.gml")
    #testRoute1
    # routeHole = getRouteFromGraph([[9.946091651916504,53.59207534790039 ],
    #                             [10.0772705078125,53.61192321777344]],graph)
    #testRoute2
    routeHole = getRouteFromGraph([[10.015552520751953,53.64086151123047 ],
                                [10.075848579406738,53.65281677246094]],graph)
    
    
    pureRoute = pruifyRoute(routeHole)
    conjList = sortNodeToConjuction(pureRoute,conj)
    traficLightsList = getRouteTraficLights(pureRoute,conj,conjList,vectorisation)
    
    dic = {"wayPoints":pureRoute,
           "conjList":conjList,
           "traficLights":traficLightsList}
    with open("testRoute07-12.json","w") as file:
        json.dump(dic,file,indent=4)

if __name__ == "__main__":
    test()
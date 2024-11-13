#!/usr/bin/env Python3
import requests
import json
from math import sqrt,acos
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
        out = ((bound[0][0] <= coord[0]) and (coord[0]<=bound[1][0]) and
               (bound[0][1] <= coord[1]) and (coord[1]<=bound[1][1]))
        return out


def getRouteConjunctionList(wayPoints:list,conjcuntions:dict)->dict:
    out = {}
    for i,wayPoint in enumerate(wayPoints):
        for name,data in conjcuntions.items():
            if len(data) ==3 and inbound(data['bound'],wayPoint):
                for point in data['junctionNodes']:
                    
                    if point == wayPoint:
                        if not name in out:
                            out[name] = []
                        out[name].append([i,point]) #alle nodes aus der conjunciton wird gesammelt
                        #data['checked'] = True

    return out


def generateVektor(pointOut:list,pointIn:list): #Vektor zeigt zum point!
    vec = [pointIn[0]-pointOut[0],pointIn[1]-pointOut[1]] #hier könnte noch der vektor normiert werden.
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

def inDegreeOffset(inputDegree, offsetDegree):
    #lowerValue,upperValue = offsetDegree-0.6108652,offsetDegree+0.6108652 #das ist ein offset von 45
    lowerValue,upperValue = offsetDegree-0.4363323,offsetDegree+0.4363323 #das ist ein offset von 25°
    return (inputDegree >= lowerValue and inputDegree <= upperValue)

def roundValues(value:float)->list:
    return (round(value*modif)/modif)

def lanesOverlape(primary:list,inDeg:list,outDeg:list)->bool:
    
    primaryInDeg,primaryOutDeg = primary[0][2],primary[2][2]
    print([inDeg,outDeg],[primaryInDeg,primaryOutDeg])
    return (inDegreeOffset(roundValues(inDeg),primaryInDeg) and inDegreeOffset(roundValues(outDeg),primaryOutDeg))

def getRouteTraficLights(route:list, conjFile:dict,conjList:list,vectorisation:dict)->list:
    traficLights,debugVector = [],[]
    skipnext = False
    for name,data in conjList.items():
        pointList    = [dat[1] for dat in data]
        pointIndex   = [dat[0] for dat in data]
        

        for primarySignal in conjFile[name]['traficLights']:
            print(primarySignal)
            meanofPoints =  vectorisation[primarySignal][1]
        #hier muessen noch index fixes gemacht werden, z.b. wenn route endet auf straße
        
            vecIn,vecOut = generateVektor(route[pointIndex[0]-1],meanofPoints),generateVektor(meanofPoints,route[pointIndex[-1]+1])
            vecOut       = [-x for x in vecOut]
            degIn,degOut = getDegree(vecIn),getDegree(vecOut)
            
            if lanesOverlape(vectorisation[primarySignal],degIn,degOut):


                traficLights.append(primarySignal)
                
                print(primarySignal)
                #break
                

    return traficLights


def pruifyRoute(route:dict)->list:
    return list(route['features'][0]['geometry']['coordinates'])



def run():
    with open("../data/conjuctionDict.json","r") as file:
        conj = json.load(file)
    
    with open("../data/vectorisation.json","r") as file:
        vectorisation = json.load(file)

    routeHole = getRoute([[9.946091651916504,53.59207534790039 ],[10.0772705078125,53.61192321777344 ]])
    pureRoute = pruifyRoute(routeHole)
    conjList = getRouteConjunctionList(pureRoute,conj)
    traficLightsList = getRouteTraficLights(pureRoute,conj,conjList,vectorisation)
    print(traficLightsList)
    
    
    dic = {"wayPoints":pureRoute,
           "conjList":conjList,
           "traficLights":traficLightsList}
    with open("route.json","w") as file:
        json.dump(dic,file,indent=4)

if __name__ == "__main__":
    run()
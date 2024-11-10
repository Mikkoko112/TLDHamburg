#!/usr/bin/env Python3
import requests
import json
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


def getRouteConjunctionList(wayPoints:list,conjcuntions:dict):
    out = []
    for wayPoint in wayPoints:
        for name,data in conjcuntions.items():
            if len(data) ==3 and inbound(data['bound'],wayPoint):
                for point in data['junctionNodes']:
                    if point == wayPoint:
                        out.append(name)
                        data['checked'] = True

    return out


def getRouteTraficLights():
    pass

def pruifyRoute(route:dict)->list:
    return list(route['features'][0]['geometry']['coordinates'])



def run():
    with open("../data/conjuctionDict.json","r") as file:
        conj = json.load(file)
    
    routeHole = getRoute([[10.015856,53.641584],[10.0894899,53.6260483]])
    pureRoute = pruifyRoute(routeHole)
    conjList = getRouteConjunctionList(pureRoute,conj)
    print(conjList)
    
    
    dic = {"wayPoints":pureRoute,
           "traficList":conjList}
    with open("route.json","w") as file:
        json.dump(dic,file,indent=4)

if __name__ == "__main__":
    run()
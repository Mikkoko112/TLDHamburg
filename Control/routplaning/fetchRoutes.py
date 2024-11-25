#!/usr/bin/env python3
import requests
import json
import igraph
import math
from geopy import distance
from timeit import default_timer as timer

def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km

def getRouteFromGraph(coordsStartEnd:list,graph:igraph.GraphBase,count:int=1)->dict:

    def getFirstLast(coordsStartEnd:list,graph:igraph.GraphBase):
        start,end = coordsStartEnd[0],coordsStartEnd[1]
        first,last = -1,-1 
        lastItemsstart,lastItemsend = [],[]
        minDistFirst,minDistLast = 1000,1000 #magic magic
        vs = graph.vs
        for i,vert in enumerate(vs): #138.40509840599952
            distStart = math.sqrt((coordsStartEnd[0][1]-vert["lat"])**2+(coordsStartEnd[0][0]-vert["lon"])**2)
            distEnd = math.sqrt((coordsStartEnd[1][1]-vert["lat"])**2+(coordsStartEnd[1][0]-vert["lon"])**2)
           
            if minDistFirst > distStart:
                first = vert["nodeid"]
                minDistFirst = distStart
            if minDistLast > distEnd:
                last = vert["nodeid"]
                minDistLast = distEnd
            #print("{:.2f}".format(i/len(vs)*100),minDistFirst,minDistLast,distStart,distEnd) #viel zu langsam

            if minDistFirst < 0.0005 and minDistLast < 0.0005: #sollte ungefähr 100 meter sein
                break

        return int(first),int(last)

    def combineRouteToGeoJson(routeList:list):
        jsonList = []
        for route in routeList:
            jsonList.append(getRoute(route))

    def convertToCoordinateRoute(routeList:list,graph)->list:
        outRoute = []
        for i,route in enumerate(routeList):
            coordRoute = []
            for node in route:
                vekt = graph.vs.select(node)
                coordRoute.append([vekt["lon"][0],vekt["lat"][0]])

            outRoute.append(coordRoute)
        return outRoute
    
    def find_closest_node(lat: float, lon: float, G: igraph.Graph):
        minimum_distance = math.inf
        minimum_node = None
        for node in G.vs:
            distance = math.sqrt((lat-node["lat"])**2+(lon-node["lon"])**2)
            if distance >= minimum_distance:
                continue
            minimum_distance = distance
            minimum_node = node["nodeid"]
        return minimum_node

    def generateGeoJsonFile(coordList:list)->dict:
        
        routelistJson = []
        latmaxList,latminList = [],[]
        logmaxList,logminList = [],[]
        for route in coordList:
            lat,log = [coord[0] for coord in route ], [coord[1] for coord in route]
            latmaxList.append(max(lat))
            latminList.append(min(lat))
            logmaxList.append(max(log))
            logminList.append(min(log))

            routelistJson.append(
             {
                "bbox":[
                    
                        min(lat),
                        min(log),
                        max(lat),
                        max(log)
                    
                ],
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": route
                },
                "properties": {
                    "name": "Example Route"
                }
            }   
            )


        return {
            "type": "FeatureCollection",
            "bbox":[
                [
                    min(latminList),
                    min(logminList),
                    max(latmaxList),
                    max(logmaxList)
                ]
            ],
            "features": routelistJson
        }
        

    
    #start = timer()
    first,last = getFirstLast(coordsStartEnd,graph)
    #print(timer()-start) #65.29947478900067
    #print(first,last)
    
    
    all_paths = graph.get_all_shortest_paths(first,to=last)
    
    #start = timer()
    coordRoutes = convertToCoordinateRoute(all_paths,graph)
    
    #print(timer()-start) #65.29947478900067
    
    geoJsonRoutes = generateGeoJsonFile(coordRoutes)
    
    with open("route.geojson","w") as file:
        json.dump(geoJsonRoutes,file, indent=4)

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

def getMultipleRoutes(coordsStartEnd:list)->dict:
    body = {"coordinates": coordsStartEnd,"alternative_routes":{"target_count":3}}
    
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

def test():
    graph = igraph.load("../data/shHamburg.gml")
    routes = getRouteFromGraph([[9.946091651916504,53.59207534790039 ],[10.0772705078125,53.61192321777344]],graph)

if __name__ == "__main__":
    test()



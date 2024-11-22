#!/usr/bin/env python3
import requests
import json
import igraph
from geopy import distance

def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km

def getRouteFromGraph(coordsStartEnd:list,graph:igraph.GraphBase,count:int=1)->dict:
    def getFirstLast(coordsStartEnd:list,graph:igraph.GraphBase):
        start,end = coordsStartEnd[0],coordsStartEnd[1]
        first,last = -1,-1
        minDistFirst,minDistLast = 1000,1000 #magic magic
        for vert in graph.vs:
            if minDistFirst > getDistanceBetweenPoints(start,[vert["lat"],vert["lon"]]):
                first = vert["node_id"]
            
            if minDistLast > getDistanceBetweenPoints(start,):
                first = vert["node_id"]
            
        return first,last

    def combineRouteToGeoJson(routeList:list):
        pass

    first,last = getFirstLast(normalRoute)
    all_paths = graph.get_all_shortest_paths(first,to=last)



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




#!/usr/bin/env python3

'''
This script is used to generate all relevant GeoJson data from the iGraph object 
provided by the control.RoutePlanner. 

Author: Helge Ramsus Steen
'''



import requests
import json
import igraph
import math
from geopy import distance
from timeit import default_timer as timer
from tldhamburg.control.routeplanning.angle_at_intersection import is_left_turn_tolerance as leftTurn
from tldhamburg.control.routeplanning.angle_at_intersection import is_right_turn_tolerance as rightTurn
from tldhamburg.control.routeplanning.models import ORSNode

def getDistanceBetweenPoints(ent:list,sr:list)->float:
    return distance.distance(ent,sr).km

def getRouteFromGraph(coordsStartEnd:list,graph:igraph.GraphBase,count:int=1)->dict:
    '''
    Input 
        <- coordsStartEnd = [[float,float],[float,float]] These are the start 
                                and end coordinate.
        <- graph          = ... This is the downloaded graph from the file
        <- count          = ... This is not used.
    
    Output 
        -> The output is a geojson route with every shortest route. 

    '''
    def getFirstLast(coordsStartEnd:list,graph:igraph.GraphBase):
        '''
        
        
        '''
        
        start,end = coordsStartEnd[0],coordsStartEnd[1]
        first,last = -1,-1 
        lastItemsstart,lastItemsend = [],[]
        minDistFirst,minDistLast = 1000,1000 #magic magic
        vs = graph.vs
        for i,vert in enumerate(vs): #138.40509840599952
            distStart = math.sqrt((coordsStartEnd[0][1]-vert["lat"])**2+
                                  (coordsStartEnd[0][0]-vert["lon"])**2)
            distEnd =   math.sqrt((coordsStartEnd[1][1]-vert["lat"])**2+
                                  (coordsStartEnd[1][0]-vert["lon"])**2)
           
            if minDistFirst > distStart:
                first = vert["nodeid"]
                minDistFirst = distStart
            if minDistLast > distEnd:
                last = vert["nodeid"]
                minDistLast = distEnd
            #This is around 100m
            if minDistFirst < 0.0005 and minDistLast < 0.0005: 
                break

        return int(first),int(last)

    def convertToCoordinateRoute(routeList:list,graph)->list:
        '''
        Input 
            <- routeList = [str,...] This is the route represented as the 
                                        node ids.
            <- graph     = ...       This is the downloaded graph
        
        Output 
            -> The output is a list of Nodes that represent the route in 
                chronological order.
                This is made out of the following components:
                [
                    lon:float,
                    lat:float,
                    nodeID:float,
                    distancefromBefore:float,
                    maxSpeed:int
                ]
        '''
        outRoute = []
        for i,route in enumerate(routeList):
            
            coordRoute = []
            distancefromBefore = 0
            for i,node in enumerate(route):
                vector = graph.vs.select(node)
                if i != 0:
                    
                    edge = graph.es.select(_source=int(pNode["nodeid"][0]),
                                           _target=int(vector["nodeid"][0]))
                    distancefromBefore = edge["length"][0]
                    if edge["maxspeed"][0] != "None" and edge["maxspeed"][0] is not None:
                        print(edge)
                        maxSpeed = int(edge["maxspeed"][0])
                    else:
                        maxSpeed = 50
                    
                    
                    pNode = vector
                else:
                    distancefromBefore = 0
                    maxSpeed = 0
                    pNode = vector
                coordRoute.append([vector["lon"][0],
                                   vector["lat"][0],
                                   node,
                                   distancefromBefore,
                                   maxSpeed])

            outRoute.append(coordRoute)
        return outRoute

    def generateGeoJsonFile(coordList:list,graph:igraph.Graph)->dict:
        '''
        Input
            -> coordList = [[[float,float,str,float,int],...],...] This is the 
                                            list of all nodes in all the Route.
            -> graph     = ...
     
        Output 
            -> The Output is a GeoJson file represented as a dict. It does not 
                        contain traffic light information.    
        '''
        routelistJson = []
        latmaxList,latminList = [],[]
        logmaxList,logminList = [],[]
        for route in coordList:
            lat,log= [coord[1] for coord in route],[coord[0] for coord in route]
            latmaxList.append(max(lat))
            latminList.append(min(lat))
            logmaxList.append(max(log))
            logminList.append(min(log))

           
            directions = []
            speeds = []
            lastSpeed,lastSpeedChangeIdx = 0,0            
            lastWayPoint = 0
            #Every route is generated separately.
            for i,node in enumerate(route): 

                #This is done to prevent out of index problems and to generate 
                # the last element.
                if i == len(route)-1: 
                    speeds.append(
                        {
                            "maxspeed":lastSpeed,
                            "way_points":[
                                lastSpeedChangeIdx,
                                len(route)-1
                            ]
                        }
                    )
                    directions.append(
                        {
                            "distance": sum([tNode[3] for tNode in route[lastWayPoint:]]), 
                            "duration": sum([tNode[3]/((5/18)*(tNode[4] if tNode[4] != 0 else 50)) for tNode in route[lastWayPoint:]]), #same here if i have time i should change this
                            "type": 10,
                            "instruction": f"Your destination is next.",
                            "name": "Goal",
                            "way_points": [
                                lastWayPoint,
                                len(route)-1
                            ]
                        }
                    )
                    
                    continue 
                #set up speed
                if lastSpeed == 0:
                    lastSpeed = node[4]
                    lastSpeedChangeIdx = 0
                
                if node[4] != lastSpeed:
                    speeds.append(
                        {
                            "maxspeed":lastSpeed,
                            "way_points":[
                                lastSpeedChangeIdx,
                                i
                            ]
                        }
                    )
                    lastSpeed = node[4]
                    lastSpeedChangeIdx = i

                #This is done to have compatibility with Stevans code 
                beforeORS = ORSNode(lat = route[i-1][1],lon = route[i-1][0],id = route[i-1][2])
                thisORS   = ORSNode(lat = node[1],lon = node[0],id = node[2])
                nextORS   = ORSNode(lat = route[i+1][1],lon = route[i+1][0],id = route[i+1][2])

                leftBool:bool  =  leftTurn(beforeORS,thisORS,nextORS)
                rightBool:bool = rightTurn(beforeORS,thisORS,nextORS)
                if leftBool or rightBool:
                    name = str(graph.es.select(_source=node[2],_target=route[i+1][2])["name"][0]) 
                    if   leftBool and not rightBool:
                        direc = "left"
                    elif not leftBool and rightBool:
                        direc = "right"
                    else:
                        direc = "Error This should not occur"
                    
                    directions.append(
                        {
                            "distance": sum([tNode[3] for tNode in route[lastWayPoint:i+1]]), 
                            "duration": sum([tNode[3]/((5/18)*(tNode[4] if tNode[4] != 0 else 50)) for tNode in route[lastWayPoint:i+1]]), 
                            "type": 0 if leftBool else 1,
                            "instruction": f"Head {direc} on {name}",
                            "name": name,
                            "way_points": [
                                lastWayPoint,
                                i+1
                            ]
                        }
                    )
                    
                    lastWayPoint = i+1 
                
                else:
                    pass


            routelistJson.append(
             {
                "bbox":[
                    
                        min(log),
                        min(lat),
                        max(log),
                        max(lat)
                    
                ],
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [coords[0:2] for coords in route]
                },
                "properties": {
                    "segments": {
                      "distance":sum([dire["distance"] for dire in directions]),
                      "duration":sum([dire["duration"] for dire in directions]),
                      "steps":directions
                    },
                    "speeds": speeds,
                    "name": "Example Route"
                }
            }   
            )

        return {
            "type": "FeatureCollection",
            "bbox":[
                [
                    min(logminList),
                    min(latminList),
                    max(logmaxList),
                    max(latmaxList)
                ]
            ],
            "features": routelistJson
        }
        

    #This gets the nearest starting node and the nearest finish node.
    first,last = getFirstLast(coordsStartEnd,graph)
    
    #This uses the inbuilt function to generate every shortest route.
    all_paths = graph.get_all_shortest_paths(first,to=last)
    
    #This converts the route into the afformentioned nodes
    coordRoutes = convertToCoordinateRoute(all_paths,graph)
    
    #This generates the GeoJson file for the route
    geoJsonRoutes = generateGeoJsonFile(coordRoutes,graph)
    
    return geoJsonRoutes

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
    '''
    Input 
        -> coordsStartEnd = [[float,float],[float,float]] These are the start 
                                and end coordinate
        
    Output
        -> The result is a GeoJson file from Open Route Service
    
    '''
    
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
    routes = getRouteFromGraph([[9.946091651916504,53.59207534790039 ],
                                [10.0772705078125,53.61192321777344]],graph)
    
    with open("route.geojson","w") as file:
        json.dump(routes,file,indent=4)

if __name__ == "__main__":
    test()



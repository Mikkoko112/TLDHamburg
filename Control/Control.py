#!/usr/bin/env python3
from routplaning import fetchRoutes as fetcher
from evaluation  import evaluation
from routplaning import routing 
import json


def test():
    testDict = {
        "coordinates":[[9.988484,53.570095 ]
                      ,[9.988844,53.566126]]
    }
    generateRoute(testDict,".")

def generateRoute(options:dict,path:str):
    data = getData(options["coordinates"])
    traficLightRoutes = routing.getTraficLightsperRoute(data)
    bestRoute = getBestRoute(traficLightRoutes)
    safeRoutes(bestRoute,path)


def safeRoutes(routeData:dict,path:str)->None:
    with open("{}/route.geojson".format(path),"w") as file:
        json.dump(routeData,file,indent=4)


def getData(coords:list)->dict:
    return fetcher.getMultipleRoutes(coords)


def getBestRoute(routeList:dict):
    route = routeList.copy()
    value = evaluation.getMinTraficLights(routeList)
    route["features"] = [routeList["features"][value]]
    return route


if __name__ == "__main__":
    test()
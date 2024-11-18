#!/usr/bin/env python3
from routplaning import fetchRoutes as fetcher
from evaluation  import evaluation
from routplaning import routing 
import json


def test():
    testDict = {
        "coordinates":[[9.946091651916504,53.59207534790039 ]
                      ,[10.0772705078125,53.61192321777344 ]]
    }
    generateRoute(testDict,".")

def generateRoute(options:dict,path:str):
    data = getData(options["coordinates"])
    traficLightRoutes = routing.getTraficLightsperRoute(data)
    with open("firstStep.json","w") as file:
        json.dump(traficLightRoutes,file,indent=4)
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
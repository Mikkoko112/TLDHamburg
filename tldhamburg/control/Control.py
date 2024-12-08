#!/usr/bin/env python3
from tldhamburg.control.routplaning import fetchRoutes as fetcher
from tldhamburg.control.evaluation  import evaluation
from tldhamburg.control.routplaning import routing 
import igraph
import json
import time
import datetime
#from tldhamburg.backend.DataFetcher import DataFetcher
#from tldhamburg.backend.Things import Things

class RoutePlaner:

    def getUpdateOnTraficLight(self,traficLightsId):
        status,nextPhase,nextPhaseTime,rapidUpdate = 0,0,0,False
        
        if isinstance(traficLightsId, list):
            out = []
            for elem in traficLightsId:
                if not isinstance(elem,list):
                    out.append(self.getUpdateOnTraficLight(elem))  
                else:
                    print("Wrong format. Input should be a list of strings")
                    exit(1)
            
            return out
        elif isinstance(traficLightsId,str):
            fetcher=DataFetcher()
            fetcher.fetch_data(params={"$filter":f"@iot.id eq '{traficLightsId}'","$expand":"Thing"})
            id=fetcher.get_data()[0]["Thing"]["@iot.id"]
            thing=Things([id])
            schaltungen=thing.get_primary_signal_observations(4,True)[id]
            zyklusDaten=thing.get_cycle_second_observations(2,True)[id]
            zyklusLänge=datetime.datetime.fromisoformat(zyklusDaten[0][0])-datetime.datetime.fromisoformat(zyklusDaten[1][0])
            zeitAktuell=datetime.datetime.fromtimestamp(time.time(),tz=datetime.timezone.utc)
            zeitGrün=(zeitAktuell-[datetime.datetime.fromisoformat(schaltung[0]) for schaltung in schaltungen if schaltung[1]==3][0])%zyklusLänge
            zeitRot=(zeitAktuell-[datetime.datetime.fromisoformat(schaltung[0]) for schaltung in schaltungen if schaltung[1]==1][0])%zyklusLänge
            status="grün" if zeitGrün>zeitRot else "rot"
            nextPhase="rot" if status=="grün" else "grün"
            nextPhaseTime=min(zeitGrün,zeitRot)
            return (traficLightsId,status,nextPhase,nextPhaseTime,rapidUpdate)

        elif isinstance(traficLightsId,int):
            return self.getUpdateOnTraficLight(str(traficLightsId))

    def safeRoute(self)->None:
        with open("{}/route.geojson".format(self.path),"w") as file:
            json.dump(self.routeData,file,indent=4)

    def _getData(self,coords:list)->dict:
        return fetcher.getMultipleRoutes(coords)

    def _getBestRoute(self,routeList:dict):
        route = routeList.copy()
        value = evaluation.getMinTraficLights(routeList)
        route["features"] = [routeList["features"][value]]
        return route

    def generateRoute(self,options:dict):
        data = self._getData(options["coordinates"])
        traficLightRoutes = routing.getTraficLightsperRoute(data)
        self.routeData = self._getBestRoute(traficLightRoutes)
        self.safeRoute()
    
    def _initMapData(self):
        with open("optionsfile.json","r") as file:
            options = json.load(file)
    
        self.graph = igraph.load(".{}".format(options["importantData"]["GraphData"]))


    def __init__(self,path:str):
        self.path = path
        self._initMapData()
        


def test():
    testDict = {
        "coordinates":[[9.988484,53.570095 ]
                      ,[9.988844,53.566126]]
    }
    routeObj = RoutePlaner(".")
    routeObj.generateRoute(testDict)

def _initMapData():
    with open("optionsfile.json","r") as file:
        options = json.load(file)
    
    return igraph.load(".{}".format(options["importantData"]["GraphData"]))

def generateRoute(options:dict,path:str,state={"called": False}):
    data = _getData(options["coordinates"])
    traficLightRoutes = routing.getTraficLightsperRoute(data)
    bestRoute = _getBestRoute(traficLightRoutes)
    _safeRoutes(bestRoute,path)

def getUpdateOnTraficLight(traficLightsId):
    status,nextPhase,rapidUpdate = 0,0,False
    
    if isinstance(traficLightsId, list):
        out = []
        for elem in traficLightsId:
            if not isinstance(elem,list):
                out.append(getUpdateOnTraficLight(elem))  
            else:
                print("Wrong format. Input should be a list of strings")
                exit(1)
        
        return out
    elif isinstance(traficLightsId,str):
        return (traficLightsId,status,nextPhase,rapidUpdate)

    elif isinstance(traficLightsId,int):
        return getUpdateOnTraficLight(str(traficLightsId))
            
def _safeRoutes(routeData:dict,path:str)->None:
    with open("{}/route.geojson".format(path),"w") as file:
        json.dump(routeData,file,indent=4)


def _getData(coords:list)->dict:
    return fetcher.getMultipleRoutes(coords)


def _getBestRoute(routeList:dict):
    route = routeList.copy()
    value = evaluation.getMinTraficLights(routeList)
    route["features"] = [routeList["features"][value]]
    return route


if __name__ == "__main__":
    test()
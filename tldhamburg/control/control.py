#!/usr/bin/env python3
from tldhamburg.control.routeplanning import fetchRoutes as fetcher
from tldhamburg.control.evaluation  import evaluation
from tldhamburg.control.routeplanning import routing 
import igraph
import json
import time
import datetime
from tldhamburg.backend.DataFetcher import DataFetcher
from tldhamburg.backend.Things import Things

class RoutePlanner:

    def getUpdateOnTrafficLight(self,trafficLightsId):
        status,nextPhase,nextPhaseTime,rapidUpdate = 0,0,0,False
        
        if isinstance(trafficLightsId, list):
            out = []
            for elem in trafficLightsId:
                if not isinstance(elem,list):
                    out.append(self.getUpdateOnTrafficLight(elem))  
                else:
                    print("Wrong format. Input should be a list of strings")
                    exit(1)
            
            return out
        elif isinstance(trafficLightsId,str):
            fetcher=DataFetcher()
            fetcher.fetch_data(params={"$filter":f"@iot.id eq '{trafficLightsId}'","$expand":"Thing"})
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
            return (trafficLightsId,status,nextPhase,nextPhaseTime,rapidUpdate)

        elif isinstance(trafficLightsId,int):
            return self.getUpdateOnTrafficLight(str(trafficLightsId))

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
        trafficLightRoutes = routing.getTrafficLightsRoute(data)
        self.routeData = self._getBestRoute(trafficLightRoutes)
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
    routeObj = RoutePlanner(".")
    routeObj.generateRoute(testDict)


if __name__ == "__main__":
    test()
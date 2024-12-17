#!/usr/bin/env python3
from tldhamburg.control.routeplanning import fetchRoutes as fetcher
from tldhamburg.control.evaluation  import evaluation
from tldhamburg.control.evaluation  import trafficlightapprox as tlapp
from tldhamburg.control.routeplanning import routing 
import igraph
import json
from datetime import datetime
import time
import datetime
from math import sqrt
from tldhamburg.backend.DataFetcher import DataFetcher
from tldhamburg.backend.Things import Things

class RoutePlanner:

    def _distBetweenPoints(self,point1ID,point2ID)->float:
        coord1 = self.routeData["features"][0]["properties"]["geometry"]["coordinate"][point1ID]
        coord2 = self.routeData["features"][0]["properties"]["geometry"]["coordinate"][point2ID]
        return sqrt(coord1[0]*coord2[0]+coord1[1]*coord2[1])


    def _casperEval(self,trafficLightsId:str):
        status,nextPhase,nextPhaseTime,rapidUpdate = 0,0,0,False
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

    def _calcSpeed(self,trafficLightsId:str,routePoint:int)->float:
        trafficLightPos = -1
        for trafficLight in self.routeData["features"][0]["properties"]["trafficlights"]:
            if trafficLight["properties"]["id"] == trafficLightsId:
                trafficLightPos =  trafficLight["properties"]["way-point"]
        
        if trafficLightPos == -1:
            print("Traffic light could not be found in the route")
            return -1

        nextSwitch = tlapp.approx_next_switch(trafficLightsId)
        now = datetime.now()

        difference = nextSwitch - now
        timeTillSwitch = difference.total_seconds()
        totalDistance  = sum([self._distBetweenPoints(p1,p1+1) 
                             for p1 in range(routePoint,trafficLightPos)])
        
        meanSpeed = totalDistance/timeTillSwitch
        
        return meanSpeed*3.6

    def getUpdateOnTrafficLight(self,trafficLightsId,curredPositionID:int = -1): #we need to add this
        status,nextPhase,nextPhaseTime,rapidUpdate,speed = 0,0,0,False,-1
        
        if isinstance(trafficLightsId, list):
            out = []
            for elem in trafficLightsId:
                if not isinstance(elem,list):
                    out.append(self.getUpdateOnTrafficLight(elem,curredPositionID))  
                else:
                    print("Wrong format. Input should be a list of strings")
                    exit(1)
            
            return out
        elif isinstance(trafficLightsId,str):
            status,nextPhase,nextPhaseTime,rapidUpdate = self._casperEval(trafficLightsId)

            if curredPositionID == -1:
                return status,nextPhase,nextPhaseTime,rapidUpdate
            else:
                speed = self._calcSpeed(trafficLightsId)
                return status,nextPhase,nextPhaseTime,rapidUpdate,speed
            #return self._casperEval(trafficLightsId)
            #return (trafficLightsId,status,nextPhase,nextPhaseTime,rapidUpdate)

        elif isinstance(trafficLightsId,int):
            return self.getUpdateOnTrafficLight(str(trafficLightsId),curredPositionID)

    def safeRoute(self)->None:
        with open("{}/route.geojson".format(self.path),"w") as file:
            json.dump(self.routeData,file,indent=4)

    def _getData(self,coords:list)->dict:
        return fetcher.getRouteFromGraph(coords,self.graph)

    def _getBestRoute(self,routeList:dict):
        route = routeList.copy()
        value = evaluation.getMinTrafficLights(routeList)
        route["features"] = [routeList["features"][value]]
        return route

    def generateRoute(self,options:dict):
        data = self._getData(options["coordinates"])
        trafficLightRoutes = routing.getTrafficLightsRoute(data)
        self.routeData = self._getBestRoute(trafficLightRoutes)
        self.safeRoute()
    
    def _initMapData(self):
        with open("tldhamburg/control/optionsfile.json","r") as file:
            options = json.load(file)
    
        self.graph = igraph.load("tldhamburg/control/{}".format(options["importantData"]["GraphData"]))


    def __init__(self,path:str):
        self.path = path
        self._initMapData()
        


def test():
    testDict = {
        "coordinates":[[10.015552520751953,53.64086151123047],
                       [10.075848579406738,53.65281677246094]]
    }
    routeObj = RoutePlanner(".")
    routeObj.generateRoute(testDict)


if __name__ == "__main__":
    test()
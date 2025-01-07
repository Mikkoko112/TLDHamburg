#!/usr/bin/env python3


'''
This file containes the RoutePlanner class that allows the frontend to 
interact with routeplanning featchers of the control. Requests and 
calulations for approximated speeds are kept ins this class.

Autor: Helge Rasmus Steen
    - _casperEval -> made py Casper

Relevant Data: 
    The Graph file is needed.

'''
from tldhamburg.control.routeplanning import fetchRoutes as fetcher
from tldhamburg.control.evaluation  import evaluation
from tldhamburg.control.evaluation import trafficlightapprox as tlapp
from tldhamburg.control.routeplanning import routing 
from tldhamburg.backend.DBMaintainer import DBMaintainer
import sqlite3

import igraph
import json
from datetime import datetime as dtime
import time
import datetime
from math import sqrt
from tldhamburg.backend.DataFetcher import DataFetcher
from tldhamburg.backend.Things import Things

class RoutePlanner:
    '''
    This class allows the frontend to generate routes wih traffic light data
    and get the approximated future phasedata for primary signals.
    
    The route is outputted as a file on a specified path.
    '''


    def _distBetweenPoints(self,point1ID:int,point2ID:int)->float:
        '''
        Input 
            <- point1ID = ... This is the first  point id
            <- point2ID = ... This is the second point id

        Output
            -> The output is the distance of the two points. 

        The Distance is measured in coordinate degree and not the 
        metric system. This is done to make quick distance calculations that 
        only need relative distances to other point pairs. Moreover this function
        uses the euclidean distance because we only observe Hamburg and this 


        '''
        coord1 = self.routeData["features"][0]["geometry"]["coordinates"][point1ID]
        coord2 = self.routeData["features"][0]["geometry"]["coordinates"][point2ID]
        return sqrt(coord1[0]*coord2[0]+coord1[1]*coord2[1])


    def _casperEval(self,trafficLightsId:str):
        status,nextPhase,nextPhaseTime,rapidUpdate = 0,0,0,False
        
        fetcher=DataFetcher()
        fetcher.fetch_data(params={"$filter":f"@iot.id eq {trafficLightsId}","$expand":"Thing"})
        id=fetcher.get_data()[0]["Thing"]["@iot.id"]

        switchTime,nextPhase=tlapp.TrafficLightApprox.approx_next_switch(id)
        status="green" if nextPhase=="red" else "red"
        zeitAktuell=dtime.fromtimestamp(time.time(),tz=datetime.timezone.utc)
        nextPhaseTime=(switchTime-zeitAktuell).total_seconds()
        return (trafficLightsId,status,nextPhase,nextPhaseTime,rapidUpdate)
        #why is this?
        thing=Things([id])
        zyklusDaten=thing.get_cycle_second_observations(2,True)[id]
        schaltungen=thing.get_primary_signal_observations(8,True)[id]
        tStart=dtime.fromisoformat(zyklusDaten[1][0])
        tEnd=dtime.fromisoformat(zyklusDaten[0][0])
        zyklusLänge=tEnd-tStart
        eventsInCycle=[(dtime.fromisoformat(zeit),state) for zeit,state in schaltungen if tStart<=dtime.fromisoformat(zeit)<=tEnd and state in [1,3]]
        
        zeitGrün=(zeitAktuell-[dtime.fromisoformat(schaltung[0]) for schaltung in schaltungen if schaltung[1]==3][0])%zyklusLänge
        zeitRot=(zeitAktuell-[dtime.fromisoformat(schaltung[0]) for schaltung in schaltungen if schaltung[1]==1][0])%zyklusLänge
        status="grün" if zeitGrün>zeitRot else "rot"
        nextPhase="rot" if status=="grün" else "grün"
        nextPhaseTime=min(zeitGrün,zeitRot)
        return (trafficLightsId,status,nextPhase,nextPhaseTime,rapidUpdate)

    def _calcSpeed(self,trafficLightsId:str,routePoint:int)->float:
        '''
        Input 
            <- trafficLightsId = ... This is the id of the looked upon primary
                                        signal
            <- routePoint      = ... This is the current position of the 
                                        driver.
        
        Output 
            -> The output is the speed that the driver approximately needs to 
                drive to reach the next traffic light in the green phase.
                The output is -1 when the traffic light could not be found.

        This function does not take into account that there could be other 
        than the given maximum speed. 
        '''
        
        def getTrafficLightIndex(routeData,trafficLightsId):

            trafficLightPos = -1
            for trafficLight in routeData["features"][0]["properties"]["trafficlights"]["features"]:
                #print(trafficLight)
                if trafficLight["properties"]["id"] == trafficLightsId:
                    trafficLightPos =  trafficLight["properties"]["way-point"]
                    break
            return trafficLightPos



        trafficLightPos = getTrafficLightIndex(self.routeData,trafficLightsId)

        if trafficLightPos == -1:
            print("Traffic light could not be found in the route")
            return -1
        
        
        i = 0
        
        totalDistance  = sum([self._distBetweenPoints(p1,p1+1) 
                            for p1 in range(routePoint,trafficLightPos)])

        if self.maxSpeed is None:
            
            sumOfSpeeds = []
            for i in range(routePoint,trafficLightPos):
                allSpeeds = self.routeData["features"][0]["properties"]["speeds"]
                for speed in allSpeeds:
                    if speed["way_points"][0] <= i <= speed["way_points"][1]:
                        sumOfSpeeds.append(speed["maxspeed"])
            self.maxSpeed = sum(sumOfSpeeds)/(abs(trafficLightPos-routePoint))

        print("_calcSpeed:",trafficLightPos,totalDistance,self.maxSpeed)
        
        fetcher=DataFetcher()
        fetcher.fetch_data(params={"$filter":f"@iot.id eq {trafficLightsId}","$expand":"Thing"})
        id=fetcher.get_data()[0]["Thing"]["@iot.id"]
        
        


        
        #print(id,trafficLightsId)
        gen = tlapp.TrafficLightApprox.approx_next_switch_generator(id)
        
        
        now                       = dtime.fromtimestamp(time.time(),
                                                    tz=datetime.timezone.utc)
        msToKmhConvert   = 3.6
        for i in range(1,1000):
            nextSwitch,nextPhase = next(gen)



            if nextPhase == "green":
                
               

                timeTillSwitch   =(nextSwitch-now).total_seconds()            

                meanMaxSpeed     = (totalDistance/timeTillSwitch)*msToKmhConvert
                
                #print(f"{meanMaxSpeed} km/h")
                
                if meanMaxSpeed  <= self.maxSpeed:
                    #This is maybe unnecessary if the next switch to a green is 
                    #always red

                    for searchForRed in range(1,1000):
                        nextRedSwitch,nextRedPhase = next(gen)
                        
                        if nextRedPhase == "red":
                            timeTillRedSwitch = (nextRedSwitch-now).total_seconds()            

                            meanMinSpeed = (totalDistance/timeTillRedSwitch)*msToKmhConvert
                            
                            return {
                                "max_speed":meanMaxSpeed,
                                "min_speed":meanMinSpeed
                            }
                    
                    return {
                                "max_speed":meanMaxSpeed,
                                "min_speed":"Could not find a red signal"
                            }
            
                i += 1

        print("No speed could be calculated")
        return -1


    def getUpdateOnTrafficLight(self,trafficLightsId,currentPositionID:int = -1): 
        '''
        Input
            <- trafficLightsId   = ...This is the primary signal or signals that
                                        are observed. This could either be one
                                        signal as a string or a list of strings.
                                        If the input is a list the output is a
                                        list of tuples and if it is a single str
                                        then the output is a tuple.
            <- currentPositionID = ...This is the index of the node the driver 
                                        is on.

        Output 
            -> status        = ... The status at the moment as a string
                                       in "green" and "red".
            -> nextPhase     = ... This is the status after the last switch
                                        in "green" and "red".
            -> nextPhaseTime = ... This is the number of seconds till the next 
                                        switch.
            -> rapidUpdate   = ... This is a bool value indicating if this 
                                        traffic light needs to be observed 
                                        often in the next time.
            -> speed         = ... This is the approximated speed the driver
                                        needs to keep to reach the next green 
                                        phase
        
        This function is still work in progress.
        '''
        print("Get status")
        status,nextPhase,nextPhaseTime,rapidUpdate,speed = 0,0,0,False,-1
        start_time = time.time()
        if isinstance(trafficLightsId, list):
            out = []
            for elem in trafficLightsId:
                if not isinstance(elem,list):
                    out.append(self.getUpdateOnTrafficLight(elem,currentPositionID))  
                else:
                    print("Wrong format. Input should be a list of strings")
                    exit(1)
            
            return out
        elif isinstance(trafficLightsId,str):
            tfLID,status,nextPhase,nextPhaseTime,rapidUpdate = self._casperEval(trafficLightsId)
            
            if currentPositionID == -1:
                return status,nextPhase,nextPhaseTime,rapidUpdate
            else:
                speed = self._calcSpeed(trafficLightsId,currentPositionID)
                print(f"--- {time.time()-start_time} s---")
                return status,nextPhase,nextPhaseTime,rapidUpdate,speed
                
            
            #return self._casperEval(trafficLightsId)
            #return (trafficLightsId,status,nextPhase,nextPhaseTime,rapidUpdate)

        elif isinstance(trafficLightsId,int):
            return self.getUpdateOnTrafficLight(str(trafficLightsId),currentPositionID)

    def safeRoute(self)->None:
        '''
        Input 
            <- None
        
        Output
            -> The output is the saved route at the point indicated at 
                self.path
        '''
        
        
        with open("{}/route.geojson".format(self.path),"w") as file:
            json.dump(self.routeData,file,indent=4)

    def _getData(self,coords:list)->dict:
        '''
        Input
            <- coords = [[float,float],[float,float]] These are the start and 
                                end coordinate
            
        Output
            -> The output is a GeoJson file represented as a dictionary.
        
        This section uses the route fetcher method.
        '''
        
        
        return fetcher.getRouteFromGraph(coords,self.graph)

    def _getBestRoute(self,routeList:dict):
        '''
        Input
            <- routeList = ... This is the generated geojson route.
        
        Output:
            -> This return a geojson file but now just containing one route.
                The evaluation now is based on the least traffic light count.
        '''
        
        route = routeList.copy()
        #value = evaluation.getMinAvgRedTime(routeList)
        value = evaluation.getMinTrafficLights(routeList)
        #removes every other route and preserve the structure of a GeoJson file.
        route["features"] = [routeList["features"][value]]
        return route

    def generateRoute(self,options:dict):
        '''
        Input
            <- options = {
                "coordinates" : [[float,float],[...]], These are the coordinates 
                    of the start and end
                "max_speed" : int                      This is the max speed for
                    speed in km/h evaluation _calcSpeed(). If this is not in the 
                    dict the default value is 50 km/h.
            
            }
        Output
            -> The output is a GeoJson file with a single route
                and traffic light data.
        '''
        
        print("Generating Route")
        start_time = time.time()
        if "max_speed" in options.keys():
            self.maxSpeed  = int(options["max_speed"]) 
        else: 
            self.maxSpeed = None
        
        print("Get Route from Graph")
        startTempTime = time.time()
        data               = self._getData(options["coordinates"])
        
        print(f"--- {time.time()-startTempTime} s---")
        print()
        
        print("Get Traffic")
        startTempTime = time.time()
        trafficLightRoutes = routing.getTrafficLightsRoute(data)
        print(f"--- {time.time()-startTempTime} s---")
        
        self.routeData     = self._getBestRoute(trafficLightRoutes)
        
        print(f"--- {time.time()-start_time} s---")
        self.safeRoute()
    
    def _initMapData(self):
        '''
        This sets up the graph data.
        '''
        print("Loading Mapdata")
        start_time = time.time()
        with open("tldhamburg/control/optionsfile.json","r") as file:
            options = json.load(file)
    
        self.graph = igraph.load("tldhamburg/control/{}".format(options["importantData"]["GraphData"]))
        print(f"--- {time.time()-start_time} s---")

    def __init__(self,path:str):
        self.path = path
        self._initMapData()
        


def test():
    testDict = {
        "coordinates":[[10.015552520751953,53.64086151123047],
                       [10.075848579406738,53.65281677246094]],
        "max_speed": 20
    }
    routeObj = RoutePlanner(".")
    routeObj.generateRoute(testDict)


if __name__ == "__main__":
    test()
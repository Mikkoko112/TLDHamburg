#!/usr/bin/env python3
import json
import sys
from shapely.geometry import box
class TrafficConjunction:
    offset = 0.0003 #i am magic puff ★now you are impressed★ puff "0.0003" klappt gut
    trafficLights:list = list()
    
    def getMinMaxLocation(self,coords)->list: 
        sm,la = [100,100],[0,0]
        for name,coord in coords:
            for j,c in enumerate(coord):
                for i,ax in enumerate(c):
                    if ax != True:    
                        if ax < sm[i]:
                            sm[i] = ax
                        if ax > la[i]:
                            la[i] = ax
        return [[sm[0],sm[1]],[la[0],la[1]]]

    def setOffset(self,coords:list)->list:
        
        sm,lm = coords[0],coords[1]
        #print(coords,sm,lm)
        of = self.offset
        return [[sm[0]-of,sm[1]-of],[lm[0]+of,lm[1]+of]]
    
    def inbound(self,coord:list)->bool: #vllt schneller, wenn Gegensatzt getestet
        out = ((self.bound[0][0] <= coord[0]<=self.bound[1][0]) and
               (self.bound[0][1] <= coord[1]<=self.bound[1][1]))
        return out

    def checkIfInBound(self,relevantORSNotes)->list:
        out = []
        #print(relevantORSNotes["nodes"])
        
        for node in relevantORSNotes["nodes"]:
            
            if  self.inbound(node["location"]):
                
                out.append(node)
        
        return out

    def __init__(self,name:str,trafficList:list,relevantORSNotes:dict):
        self.trafficLights = [name[0] for name in trafficList]
        self.bound = self.setOffset(self.getMinMaxLocation(trafficList))
        self.junctionNodes = self.checkIfInBound(relevantORSNotes)
        self.name = name
    
    def returnValue(self)->tuple:
        node = self.junctionNodes
        if len(sys.argv) == 1:
            node = [name["location"]for name in self.junctionNodes]
        
        return (self.name,node,list(set(self.trafficLights)),self.bound)


def run():
    with open("../data/combinedHoleData.json","r") as file:
        notes = json.load(file)
    with open("../data/conjunctionsJoint.json","r") as file:
        conj = json.load(file)
    with open("../data/fetchAreasFullDataRerun.json","r") as file:
        fetchAreas = json.load(file)
    
    with open("../data/thingsLoc.json","r") as file:
        origData = json.load(file)

    trafficConjunctionList = []
    outDict = {}
    conjCOunt = 0

    # for conjunctionName,conjunction in conj.items():    #Geht über die Conjunctions
        
    #     for areaName,area in fetchAreas.items():        #Geht über alle relevanten Bereiche
    #         # if(conjunctionName == "21851"):
    #         #             print("part of missing data")
    #         for nodeInArea in area[1]:                  #Geht über jede Ampel im Area --!!!! dies muss geaendert werden zu einem bound check!!!
    #             if areaName != "13937" and  nodeInArea[0] == conjunctionName:    #Wenn die Conjunction in der Area ist
                    
    #                 conjCOunt+=1
    #                 trafficList =  conjunction[1]
    #                 relevantORSNotes = notes[areaName]
    #                 trafficConjunctionList.append(TrafficConjunction(conjunctionName,trafficList,relevantORSNotes))

    allPrimarySignals = []
    misstConj = []
    for conjunctionName,conjunction in conj.items():
        used = False
        coord1 = conjunction[0]
        conjBox = box(coord1[0][0],coord1[0][1],coord1[1][0],coord1[1][1]) 
        
        for areaName,area in fetchAreas.items():
            coord2 = area[0]
            areaBox = box(coord2[0][0],coord2[0][1],coord2[1][0],coord2[1][1]) 
        
            if (conjBox.contains(areaBox) or areaBox.contains(conjBox)):
                conjCOunt+=1
                trafficList =  conjunction[1]
                for conj in conjunction[1]:
                    allPrimarySignals.append(conj[0])
                relevantORSNotes = notes[areaName]
                trafficConjunctionList.append(TrafficConjunction(conjunctionName,trafficList,relevantORSNotes))
                used = True
        if not used:
            misstConj.append(conjunctionName)
    
    keys = origData.keys()
    print(len(keys),len(allPrimarySignals))
    lostData = list(set(keys) - set(allPrimarySignals))
    print(lostData)
    print(len(lostData))
    print(misstConj)
    for conjunctionObject in trafficConjunctionList:
        name,junctionNodes,trafficLights,bound = conjunctionObject.returnValue()
        # if(name == "21851"):
        #     print(name,trafficLights,bound)
        outDict[name] = {"bound"        :bound,
                         "junctionNodes":junctionNodes,
                         "trafficLights" :trafficLights}
    
    #print(conjCOunt,len(conj))
    with open("../data/conjunctionDict.json","w") as file:
        json.dump(outDict, file, indent=4)    

if __name__ == "__main__":
    run()
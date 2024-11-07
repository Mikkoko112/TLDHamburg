#!/usr/bin/env python3
import json

class TraficConjunction:
    offset = 0.01
    traficLights:list = list()
    
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
        print(coords,sm,lm)
        of = self.offset
        return [[sm[0]-of,sm[1]-of],[sm[0]+of,sm[1]+of]]
    
    def inbound(self,coord:list)->bool: #vllt schneller, wenn Gegensatzt getestet
        out = ((self.bound[0][0] <= coord[0]) and (coord[0]<=self.bound[1][0]) and
               (self.bound[0][1] <= coord[1]) and (coord[1]<=self.bound[1][1]))
        return out

    def checkIfInBound(self,relevantORSNotes)->list:
        out = []
        print(relevantORSNotes["nodes"])
        
        for node in relevantORSNotes["nodes"]:
            exit()
            if  self.inbound(node["location"]):
                out.append(node)
        print(out)
        return out

    def __init__(self,name:str,traficList:list,relevantORSNotes:dict):
        self.traficLights = traficList
        self.bound = self.setOffset(self.getMinMaxLocation(traficList))
        self.junctionNodes = self.checkIfInBound(relevantORSNotes)
        self.name = name
    
    def returnValue(self)->tuple:
        return (self.name,self.junctionNodes,self.traficLights)


def run():
    with open("holeData.json","r") as file:
        notes = json.load(file)
    with open("../data/conjunctionsJoint.json","r") as file:
        conj = json.load(file)
    with open("../data/fetchAreasFullData.json","r") as file:
        fetchAreas = json.load(file)

    traficConjunctionList = []
    outDict = {}
    conjCOunt = 0
    for conjunctionName,conjunction in conj.items():
        
        for areaName,area in fetchAreas.items():
        
            for noteInArea in area[1]:
                if noteInArea[0] == conjunctionName:
                    print(areaName,noteInArea[0],conjunctionName)
                    conjCOunt+=1
                    traficList =  conjunction[1]
                    relevantORSNotes = notes[areaName]
                    print(len(relevantORSNotes))
                    #print(relevantORSNotes)
                    traficConjunctionList.append(TraficConjunction(conjunctionName,traficList,relevantORSNotes))
    
    print(traficConjunctionList)
    
    '''
    for conjunctionObject in traficConjunctionList:
        name,junctionNodes,traficLights = conjunctionObject.returnValue()
        outDict[name] = {"junctionNodes":junctionNodes,
                         "traficLights":traficLights}
    
    print(conjCOunt,len(conj))
    with open("../data/conjuctionDict.json","w") as file:
        json.dump(outDict, file, indent=4)    '''

if __name__ == "__main__":
    run()
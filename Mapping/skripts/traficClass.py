

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
                        elif ax > la[i]:
                            la[i] = ax
        return [[sm[0],sm[1]],[la[0],la[1]]]

    def setOffset(self,coords:list)->list:
        sm,lm = coords[0],coords[1]
        of = self.offset
        return [[sm[0]-of,sm[1]]-of,[sm[0]+of,sm[1]+of]]
    
    def inbound(self,coord:list)->bool: #vllt schneller, wenn Gegensatzt getestet
        out = ((self.bound[0][0] <= coord[0]) and (coord[0]<=self.bound[1][0]) and
               (self.bound[0][1] <= coord[1]) and (coord[1]<=self.bound[1][1]))
        return out

    def checkIfInBound(self,relevantORSNotes)->list:
        out = []
        for name,node in relevantORSNotes:
            if  self.inbound(node["location"])
                out.append([name,node])
        
        return out

    def generateDirections(self, traficList)->dict:
        pass
    
    def __init__(self,traficList:list,relevantORSNotes:dict):
        self.traficLights = traficList
        self.bound = self.setOffset(self.getMinMaxLocation(traficList))
        self.junctionNodes = self.checkIfInBound(relevantORSNotes)
        

    
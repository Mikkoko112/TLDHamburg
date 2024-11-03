

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
        return [[sm[0],la[1]],[la[0],sm[1]]]

    def setOffset(self,coords:list)->list:
        sm,lm = coords[0],coords[1]
        of = self.offset
        return [[sm[0]-of,sm[1]]-of,[sm[0]+of,sm[1]+of]]
    
    def chechIfInBound(self,relevantORSNotes)->list:
        out = []
        for i,note in relevantORSNotes:
            if true #hier noch einfügen
        
        return out

    def generateDirections(self, traficList)->dict:
        pass
    
    def __init__(self,traficList:dict,relevantORSNotes:dict):
        self.traficLights = traficList
        self.bound = self.setOffset(self.getMinMaxLocation(traficList))
        

    
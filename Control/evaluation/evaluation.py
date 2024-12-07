
'''
to define a new function, follow the template.
'''

def getMinTraficLights(routeListDict:dict)->int:
    routeList = routeListDict["features"]
    minCount,idx = 0,0
    for i,route in enumerate(routeList):
        traficLights = route["properties"]["traficlights"]["features"]
        if minCount == 0:
            minCount = len(traficLights)
            idx = i
        if minCount < len(traficLights):
            minCount = len(traficLights)
            idx = i
    return idx
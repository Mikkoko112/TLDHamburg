
'''
to define a new function, follow the template.
'''

def getMinTrafficLights(routeListDict:dict)->int:
    routeList = routeListDict["features"]
    minCount,idx = 0,0
    for i,route in enumerate(routeList):
        trafficLights = route["properties"]["trafficlights"]["features"]
        if minCount == 0:
            minCount = len(trafficLights)
            idx = i
        if minCount < len(trafficLights):
            minCount = len(trafficLights)
            idx = i
    return idx
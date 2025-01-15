from tldhamburg.control.control import RoutePlanner
import json
import time
testDict = {
    "coordinates":[[9.9885268,53.5573318],
                   [10.085635385830994,53.558576099999996 ]],
    "max_speed"  : 50,
    "static_analysis" : "phases"
}


def makeKCallsPerSecond(k:int,trafficLightId:str,routeObj):
    print(f"{1/k:.2f}s")
    for i in range(0,15):
        routeObj.getUpdateOnTrafficLight(trafficLightId,currentPositionID=1)
        time.sleep(1/k)


routeObj = RoutePlanner(".")
routeObj.generateRoute(testDict)

'''start = time.time()
makeKCallsPerSecond(5,"3440",routeObj)
print(time.time()-start)'''
del routeObj
exit()

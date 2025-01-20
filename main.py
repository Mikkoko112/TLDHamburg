from tldhamburg.control.control import RoutePlanner
import json
import time
testDict = {
    "coordinates":[[9.9885268,53.5573318],
                   [10.085635385830994,53.558576099999996 ]],
    "max_speed"  : 50,
    "static_analysis" : "phases"
}

start    = time.time()

routeObj = RoutePlanner(".")
print(f"{time.time()-start:.2f}s")

routeObj.generateRoute(testDict)

print(routeObj.getUpdateOnTrafficLight("1997",1))

'''start = time.time()
makeKCallsPerSecond(5,"3440",routeObj)
print(time.time()-start)'''
del routeObj
exit()

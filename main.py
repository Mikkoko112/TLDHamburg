from tldhamburg.control.control import RoutePlanner
import json
import time
testDict = {
    "coordinates":[[9.9853126,53.5678859],
                   [10.0084222,53.5524079 ]],
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

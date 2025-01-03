from tldhamburg.control.control import RoutePlanner
 

testDict = {
    "coordinates":[[9.946091651916504,53.59207534790039],
                   [10.0772705078125,53.61192321777344 ]]
}
routeObj = RoutePlanner(".")
routeObj.generateRoute(testDict)

print(routeObj.getUpdateOnTrafficLight(14310,currentPositionID=1))


del routeObj
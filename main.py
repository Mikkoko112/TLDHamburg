from tldhamburg.control.control import RoutePlanner
import json

testDict = {
    "coordinates":[[9.946091651916504,53.59207534790039],
                   [10.0772705078125,53.61192321777344 ]],
    "max_speed"  : 50 
}

testDict = {
    "coordinates":[[9.946091651916504,53.59207534790039],
                   [10.0772705078125,53.61192321777344 ]]
}
routeObj = RoutePlanner(".")
routeObj.generateRoute(testDict)
'''
notWoringPrimarySignals = [14897, 21950, 14317, 16963, 22277, 22472]
for wrongSignal in notWoringPrimarySignals[::-1]:
    print(wrongSignal)
    print(routeObj.getUpdateOnTrafficLight(wrongSignal,currentPositionID=1))
del routeObj

'''
#simply checking all Primary signals in the route.
couldNotUse = []
with open("route.geojson","r") as file:
    route = json.load(file)

for trafficLight in route["features"][0]["properties"]["trafficlights"]["features"]:
    try:
        print(routeObj.getUpdateOnTrafficLight(int(trafficLight["properties"]["id"]),currentPositionID=1))
    except (ValueError,TypeError) as e:
        print(int(trafficLight["properties"]["id"]),"Could not find")
        couldNotUse.append(int(trafficLight["properties"]["id"]))


print(couldNotUse,len(route["features"][0]["properties"]["trafficlights"]["features"]))

del routeObj
exit()

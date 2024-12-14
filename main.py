from tldhamburg.control.control import RoutePlanner


testDict = {
    "coordinates":[[10.013066,53.62795],
                    [10.075848579406738,53.65281677246094]]
}
routeObj = RoutePlanner(".")
routeObj.generateRoute(testDict)

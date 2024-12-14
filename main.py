from tldhamburg.control.control import RoutePlanner


testDict = {
    "coordinates":[[10.015552520751953,53.64086151123047],
                    [10.075848579406738,53.65281677246094]]
}
routeObj = RoutePlanner(".")
routeObj.generateRoute(testDict)


'''
to define a new function, follow the template.
'''
from .trafficlightapprox import TrafficLightApprox

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

def getMinAvgRedTime(routeList: dict, support_points: int = 20) -> int:
    """
    Find the best route by statistical estimation of red-phases.
    We estimate the mean % of red-time for each traffic light along the route,
    then use the sum of these estimations as a weighting function.

    Args:
        routeList (dict): A list of GeoJSON route objects
        support_points (int): How many recent observations to use for wait-time estimation.

    Returns:
        If a route with estimated wait-time smaller than infinity can be found:
            int: index of the route with lowest estimated wait time
    Raises:
        RuntimeError: if a route with wait-time less than infinity cannot be found
    """
    routeList = routeListDict["features"]
    minIndex = -1
    minWeight = float("inf")

    for i, route in enumerate(routeList):
        trafficLights = route["properties"]["trafficlights"]["features"]
        routeWeight = 0
        for light in trafficLights:
            light_id = int(light["properties"]["id"])
            green, red = TrafficLightApprox.mean_light_phases(light_id, support_points)
            redRatio = red/(green+red)
            routeWeight += redRatio
        if routeWeight < minWeight:
            minIndex = i
            minWeight = routeWeight
    # if minIndex is still -1 here, then something went wrong.
    if minIndex == -1:
        raise RuntimeError(f"getMinAvgRedTime({routeList}, {support_points}) error:\n"
                           "All routes in the input dictionary have infinite wait-time estimates.")
    return MinIndex

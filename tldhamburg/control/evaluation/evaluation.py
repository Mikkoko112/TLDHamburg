"""
to define a new function, follow the template.
"""

import sys
from tldhamburg.backend.DataFetcher import DataFetcher
from .trafficlightapprox import TrafficLightApprox


def getMinTrafficLights(routeListDict: dict) -> int:
    """
    Input
        <- routeListDict = ...          This is the list of Routes in form of a
                GeoJson file.


    Output
        -> idx = int                    This is an index for the route dict.

    This function will return the index of the route with the least traffic
    lights
    """
    routeList = routeListDict["features"]
    minCount, idx = -1, 0
    if len(routeList) == 1: 
        return 0
    
    for i, route in enumerate(routeList):
        trafficLights = route["properties"]["trafficlights"]["features"]
        if minCount == -1:
            minCount = len(trafficLights)
            idx = i
        if minCount > len(trafficLights):
            minCount = len(trafficLights)
            idx = i
    return idx


def getMinAvgRedTime(routeListDict: dict, support_points: int = 20) -> int:
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
        If this is not the case, the getMinTrafficLights function is called.
    """
    routeList = routeListDict["features"]
    minIndex = -1
    minWeight = float("inf")
    if len(routeList) == 1: 
        return 0
    
    for i, route in enumerate(routeList):
        trafficLights = route["properties"]["trafficlights"]["features"]
        routeWeight = 0

        for light in trafficLights:
            
            try:
                
                # green, red = TrafficLightApprox.mean_light_phases(light_id, support_points)
                trafficLightID = int(light["properties"]["id"])

                meanOutput = TrafficLightApprox.mean_light_phases(trafficLightID, support_points)
                if meanOutput is None:
                    
                    continue
                green, red = meanOutput[0], meanOutput[1]

                # We use r²/(r+g) as an estimate of dimension "Time".
                # We want to weight lights with longer red phases more heavily,
                # but also take into account how fast they will switch to green.
                # The formula r(r/(r+g)) is a natural result of this idea.
                redRatio = (red * red) / (green + red)
                routeWeight += redRatio
            except TypeError:
                print(f"Could not load data from {light}:")
                sys.exc_info()

        if routeWeight < minWeight:
            minIndex = i
            minWeight = routeWeight
    # if minIndex is still -1 here, then something went wrong.
    if minIndex == -1:
        return getMinTrafficLights(routeListDict)
        # raise RuntimeError(
        #     f"getMinAvgRedTime({routeList}, {support_points}) error:\n"
        #     "All routes in the input dictionary have infinite wait-time estimates."
        # )
    
    return minIndex

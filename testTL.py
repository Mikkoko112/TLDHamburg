from pathlib import Path
import json
from bisect import bisect_right
# from tldhamburg.control.control import RoutePlanner
from tldhamburg.frontend.Navigation import Navigation
from tldhamburg.frontend.position import Position
from tldhamburg.control.control import RoutePlanner
import time

path = f"{Path.cwd()}/schnittstelle"
departure, destination = [9.98373,53.564093], [9.974259,53.567634]
start_end = {"coordinates": [departure,destination]}

navigate = Navigation()
navigate.create_route(departure, destination)


list_waypoints = navigate.way_points
pos = Position()
lat, lon = list_waypoints[0]
# lat = lat + 0.01
# lon = lon + 0.01
pos.set_pos(lat, lon)
navigate.update_route(pos)
print(f"status: {navigate.status_next_tl}, recommended speed: {navigate.current_recommended_speed}")

# things_id_list = []
# for trafficlight in navigate.trafficlights:
#     things_id_list.append(trafficlight.things_id)
# for key in list(trafficlights.keys()):
#     navigate._update_trafficlight(navigate.trafficlights[key])

for lat, lon in list_waypoints:
    pos.set_pos(lat, lon)
    navigate.update_route(pos)
    print(f"status: {navigate.status_next_tl}, recommended speed: {navigate.current_recommended_speed}")


# print(f"status = {color}") # color of current phase
# print(f"nextPhase = {nextPhase}") # color of next phase green/red
# print(f"nextPhaseTime = {nextPhaseTime}") # in seconds
# print(f"rapidUpdate = {rapidUpdate}") # bool
# print(f"speed = {speed}") # km/h


# end = time.time()
# print(f"duration Rasmus+Harry {end-begin}")

# pos.set_pos(lat, lon)
# navigate.start_navigation(pos)
# navigate.is_on_route(pos)
# for i in range(1, len(list_waypoints)):
#     lat, lon = list_waypoints[i]
#     pos.set_pos(lat,lon)
#     navigate.update_route(pos)


# pos.set_pos(9.97728824615479,53.5637016296387)
# navigate.update_route(pos)
# navigate._update_trafficlight(navigate.trafficlights[23])

# print(f"total distance = {navigate.total_distance}")
# print(f"last distance = {navigate.distance_integral[-1]}")
# print(f"coordinates = {navigate.geojson['features'][0]['geometry']['coordinates']}")



# start_end = {"coordinates": [[9.98373,53.564093],[9.974259,53.567634]]}

# new_route = RoutePlanner(path)
# new_route.generateRoute(start_end)   




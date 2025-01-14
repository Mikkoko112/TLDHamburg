import json
import logging
import numpy as np
from numpy import pi
from pathlib import Path
from tldhamburg.frontend.position import Position
from tldhamburg.frontend.trafficlights import Trafficlight
from tldhamburg.control.control import RoutePlanner
import geopy.distance
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from bisect import bisect_right

class Navigation:
    """
    documentation

    directions are the navigation instructions e.g. when and where to turn left
    """
    _path = None
    _route = None            # of class Route
    departure = None
    destination = None
    start_navigating = True 
    route_deviation_tolerance = 200 # in meters

    geojson = None          # actual content of geojson file
    
    way_points = []         # list of coordinates representing the route
    way_points_lon_lat = [] # coordinates lat, lon turned
    distance_integral = []  # accumulated distance
    duration_integral = []  # accumulated approx. time
    speed_limits = {}       # dict of ascending waypoints and associated speed limits
    trafficlights = {}     # dict of ascending waypoints and associated traffic lights

    # dict of waypoints and associated navigation instructions (directions) as well as distance and duration data
    navigation_instructions = {} 
    total_distance = None
    total_duration = None
    
    current_position = Position() # does not have to be a point on the route
    
    current_way_point_index = None # idx of nearest way point on route to current position
    current_speed_limit = None

    current_nav_instr_text = None # navigation text e.g. "turn left"
    current_nav_instr_picture = None # associated picture
    remaining_distance = None
    remaining_nav_instr_texts = []
    remaining_nav_instr_distances = []
    
    current_progress_next_tl = None # progress to next traffic light
    next_tl = None          # Trafficlight Object
    status_next_tl = "" # status for the next trafficlight 
    current_recommended_speed = None # speed recommened 
    next_next_tl = None

    bicycle_mode = False

        
    def __init__(self, path=f"{Path.cwd()}/schnittstelle"):
        self._path = path
        self._route = RoutePlanner(self._path)
    
    def create_route(self, departure:list, destination:list):
        # instruct creation of route
        self.departure = departure
        self.destination = destination
        if self.bicycle_mode is True:
           nav_coordinates = {"coordinates": [departure,destination],
                              "max_speed": 20} 
        else:
            nav_coordinates = {"coordinates": [departure,destination]}
        self._route.generateRoute(nav_coordinates)

        # route is saved as a geojson file. Load it...
        self.geojson = self._init_route_geojson()

        # build static data of the route
        self.way_points, self.way_points_lon_lat = self._init_waypoints()
        self.navigation_instructions = self._init_navigation_instructions()
        try:
            self.speed_limits = self._init_speed_limits()
        except (KeyError):
            self.speed_limits = None
        try:
            self.trafficlights = self._init_traffic_lights()
        except (KeyError):
            self.trafficlights = None
        
        # initialize instruction list
        remaining_nav_instr_texts = []
        remaining_nav_instr_distances = []
        for key, step in self.navigation_instructions.items():
            remaining_nav_instr_texts.append(step["instruction"])
            remaining_nav_instr_distances.append(round(step["distance"]))
        self.remaining_nav_instr_texts = remaining_nav_instr_texts
        self.remaining_nav_instr_distances = remaining_nav_instr_distances

        # initialize dynamic data of the route based on starting way_point
        self.current_way_point_index = 0
        self.current_speed_limit = self._get_current_speed_limit()
        nav_instr_key = self._get_current_navigation_instruction_key()
        (self.current_nav_instr_text, 
         self.current_nav_instr_picture, 
         _, 
         _, 
         _) = (
             self.load_navigation_instruction(nav_instr_key)
             )
        self.next_tl, self.next_next_tl = self._get_impending_two_trafficlights()


 
    def _init_route_geojson(self):
        """loads dict(route) that was created"""
        with open(f"{self._path}/route.geojson", "r") as f:
            route_geojson = json.load(f)
        return route_geojson

    def _init_navigation_instructions(self):
        """
        in: geojson file
        out: direction instructions, corresponding pictures, endpoints list
        """
        route = self.geojson
        # https://github.com/GIScience/openrouteservice-docs#instruction-types
        '''dictionary = {0: "Left", 1: "Right", 2: "Sharp left", 3: "Sharp right",
                    4: "Slight left", 5: "Slight right", 6: "Straigth",
                    7: "Enter roundabout", 8: "Exit roundabout", 9: "U-turn",
                    10: "Goal", 11: "Depart", 12: "Keep left" , 13: "Keep right"}
        '''
        # map the type Ids to the right picture
        dic_directions = {0: "turn_left.png", 1: "turn_right.png", 
                        2: "turn_slight_left.png", 3: "turn_slight_right.png", 
                        4: "turn_slight_left.png", 5: "turn_slight_right.png", 
                        6: "straight.png", 7: "Enter roundabout", 
                        8: "straight.png", 9: "U_turn.png", 10: "straight.png",  #changed goal to straight
                        11: "straight.png", 12: "keep_left.png" , 13: "keep_right.png"}
        dic_roundabouts = {1: "roundabout_right.png", 2: "roundabout_straight.png", 
                        3: "roundabout_left.png"}
        
        navigation_instructions = {}

        """
        # determine distances between points SHAPELY
        distance_integral = []
        lat, lon = self.way_points[0]
        last_point = Point(lat, lon)
        for lat, lon in self.way_points:
            next_point = Point(lat, lon)
            distance = last_point.distance(next_point)
            print(f"distance last, next: {distance}")
            distance_integral.append(distance)
            last_point = next_point
        print(f"total distance: {distance_integral[-1]}")
        total_distance = distance_integral[-1]
        
        total_duration = 0
        # duration_integral = [0]
        """

        # determine distances between points Geopy
        distance_integral = []
        last_point = self.way_points_lon_lat[0]
        for i, next_point in enumerate(self.way_points_lon_lat):
            distance = geopy.distance.geodesic(last_point, next_point).meters
            if i == 0:
                distance_integral.append(distance)
            else:
                distance_integral.append(distance_integral[i-1] + distance)
            last_point = next_point
        total_distance = distance_integral[-1]
        
        total_duration = 0
        # duration_integral = [0]


        steps = route["features"][0]["properties"]["segments"]["steps"]
        for step in steps:
            total_distance = total_distance + step["distance"]
            total_duration = total_duration + step["duration"]
            val = dic_directions[step["type"]]
            if val == "Enter roundabout":
                val = dic_roundabouts[step["exit_number"]]
            # create dictionary of instructions. 'key' is the last waypoint of given section 
            num_waypoints = step["way_points"][1] - step["way_points"][0]
            navigation_instructions[step["way_points"][1]] = {
                "instruction": step["instruction"], 
                "picture": val, 
                "distance": step["distance"], 
                "duration": step["duration"],
                "num_waypoints": num_waypoints # overlapping waypoints between steps
                }

            """
            # assuming approx. equal distance between waypoints of given step
            # this was a very bad assumption. It does not reflext how it works... nice try
            if num_waypoints == 0:
                distance_per_waypoint = 0
                duration_per_waypoint = 0
            else:
                distance_per_waypoint = round(step["distance"] / num_waypoints, 3)
                duration_per_waypoint = round(step["duration"] / num_waypoints, 3)
            start_idx = len(distance_integral)
            end_idx = start_idx + num_waypoints
            # print(f"num_waypoints = {num_waypoints}, distance = {step["distance"]}\n dist_per_wp = {distance_per_waypoint}")
            for i in range(start_idx, end_idx):
                if start_idx == 0:
                    distance_integral.append(0)
                    duration_integral.append(0)
                else:
                    distance_integral.append(distance_integral[i-1] + distance_per_waypoint)
                    duration_integral.append(duration_integral[i-1] + duration_per_waypoint)
                    # print(f"last: {distance_integral[i-1]} add {distance_per_waypoint} = {distance_integral[i]} (at pos {i})")
        """
            
        # if len(self.way_points) == len(distance_integral):
        self.distance_integral = distance_integral
        # self.duration_integral = duration_integral
        self.total_distance = total_distance
        self.total_duration = total_duration

        return navigation_instructions

    def _init_waypoints(self):
        waypoints_lat_lon = self.geojson['features'][0]['geometry']['coordinates']
        waypoints_lon_lat = []
        for lat, lon in waypoints_lat_lon:
            waypoints_lon_lat.append([lon, lat])
        return waypoints_lat_lon, waypoints_lon_lat

    def _init_speed_limits(self):
        maxspeeds = self.geojson['features'][0]['properties']['speeds']
        maxspeeds_dict = {}
        for step in maxspeeds:
            maxspeeds_dict[step["way_points"][1]] = step["maxspeed"]
        return maxspeeds_dict

    def _init_traffic_lights(self):
        trafficlights = self.geojson["features"][0]["properties"]["trafficlights"]["features"]
        trafficlights_dict = {}
        for trafficlight in trafficlights:
            trafficlights_dict[trafficlight["properties"]["way-point"]] = Trafficlight(
                trafficlight["properties"]["id"],
                trafficlight["geometry"]["coordinates"][0], # lat
                trafficlight["geometry"]["coordinates"][1], # lon
                trafficlight["properties"]["object"])
        return trafficlights_dict

    def is_on_route(self, current_position:Position):
        """
        Check if the current position is on or near the route.
        in: position(lat,lon)
        out: bool(on_route)
        Adjust tolerance in settings 'route_deviation_tolerance'
        """
        # determine nearest point within route
        lat, lon = current_position.get_pos()
        point = Point(lat, lon)
        route = LineString(self.way_points)
        nearest_way_point = nearest_points(route, point)[0]
        
        # determine min distance to route
        current = (lon, lat)
        lat, lon = nearest_way_point.x, nearest_way_point.y
        nearest = (lon, lat)
        distance = geopy.distance.geodesic(current, nearest).meters
        on_route = distance <= self.route_deviation_tolerance
        if on_route == False:
            logging.info(f"distance to route: {distance}, tolerance: {self.route_deviation_tolerance}\n\tcurrent Position: {lat, lon}\n\tnearest point: {nearest_way_point}")

        return on_route
    
    def _haversine_approx(self, lat1, lon1, lat2, lon2):
        """
        Approximate distance between two points using haversine formular.
        """
        x = (lon2 - lon1) * (pi / 180.0)  
        y = (lat2 - lat1) * (pi / 180.0)  
        return (x ** 2 + y ** 2) ** 0.5  
    
    def _get_current_waypoint_index(self):
        """determine nearest waypoint"""
        lat, lon = self.current_position.get_pos()
        distances = np.array([self._haversine_approx(lat, lon, lat_wp, lon_wp) for lat_wp, lon_wp in self.way_points])
        nearest = np.argmin(distances)
        return nearest

    def _get_current_navigation_instruction_key(self):
        """
        determines next navigation instruction key
        based on the current waypoint index
        """
        keys_list = list(self.navigation_instructions.keys())
        idx = bisect_right(keys_list, self.current_way_point_index)
        try:
            key = keys_list[idx]
        except (ValueError, IndexError): # if there is no further instruction, use last.
            key = keys_list[idx-1]
        return key
    
    def load_navigation_instruction(self, key):
        """
        in: key (of trafficlights dictionary)
        out: 5-tuple instruction data
        """
        instruction_step = self.navigation_instructions[key]
        text = instruction_step["instruction"]
        picture = instruction_step["picture"]
        distance = instruction_step["distance"]
        duration = instruction_step["duration"]
        num_waypoints = instruction_step["num_waypoints"]
        return text, picture, distance, duration, num_waypoints

    def _get_current_speed_limit(self):
        """
        determines speed limit based on the current waypoint index
        """
        if self.speed_limits is not None:
            keys_list = list(self.speed_limits.keys())
            if self.current_way_point_index in keys_list: # we are at a traffic light
                key = self.current_way_point_index
            else:
                idx = bisect_right(keys_list, self.current_way_point_index)
                try:
                    key = keys_list[idx]
                except (ValueError, IndexError): # we have passed all traffic lights on our route
                    # Speedlimit could not be found. Probably the data is incomplete. Check the route.geojson file.
                    return 0
            return self.speed_limits[key]
        else:
            return self.current_speed_limit

    def _get_impending_two_trafficlights(self):
        """
        in: dict(trafficlights), int(current_waypoint_index)
        out: upcoming two traffic lights: 'next_tl' and 'next_next_tl'
        """
        if self.trafficlights is not None:
            tl_keys = list(self.trafficlights.keys())
            try:
                key_idx = bisect_right(tl_keys, self.current_way_point_index)
                key_next_tl = tl_keys[key_idx]
                next_tl = self.trafficlights[key_next_tl]
            except (ValueError, IndexError): 
                next_tl = None

            try:
                key_second_next_tl = tl_keys[key_idx + 1]
                second_next_tl = self.trafficlights[key_second_next_tl]
            except (ValueError, IndexError):
                second_next_tl = None
            return next_tl, second_next_tl
        else:
            return None, None
        
    def _update_trafficlight(self, trafficlight:Trafficlight):
        """
        Updates the status of the Trafficlight object and updates the speed
        recommendation if trafficlight is the next one 
        """
        # TODO umbauen
        # color,_,_,_,speed
        color,nextPhase,nextPhaseTime,rapidUpdate,speed= (        
            self._route.getUpdateOnTrafficLight(trafficlight.things_id, self.current_way_point_index))
        set_color = trafficlight.set_status(color)
        if trafficlight == self.next_tl:
            self.status_next_tl = set_color
            self._update_recommended_speed(color,speed)

        # TODO ausbauen
        #print(f"id = {trafficlight.things_id}, status = {color}, nextPhase = {nextPhase}, nextPhaseTime = {nextPhaseTime}, rapidUpdate = {rapidUpdate}, speed = {speed}")
    
    def _update_recommended_speed(self, color, speed):
        """
        Updates recommended speed in km/h
        status 'green': use min speed necessary to cross trafficlight before change
        status 'red': use max speed to avoid stopping at the traffic light
        """
        if speed == -1:
            recommended = "-"
        else:
            if color == "green":
                recommended = speed["min_speed"]
            elif color == "red":
                recommended = speed["max_speed"]
            else:
                recommended = 0

            if recommended > self.current_speed_limit:
                recommended = self.current_speed_limit
            elif recommended < 0:
                recommended = 0

            recommended = round(recommended, ndigits=0)
        self.current_recommended_speed = recommended
        return recommended

    def start_navigation(self, position:Position):
        """
        toggles navigation to start if sensible
        requires position to be within 'route_deviation_tolerance'
        """
        if self.is_on_route(position) == False:
            self.start_navigating = False
            return False
        else:
            self.start_navigating = True
            self.update_route(position)
            return True

    def _update_status_bar(self):
        """shows progress in percent to next trafficlight"""
        tl_keys = list(self.trafficlights.keys())
        if self.current_way_point_index in tl_keys: # we are at a traffic light
            next_reference_waypoint = self.current_way_point_index
            tl_right_idx = tl_keys.index(next_reference_waypoint)
        else:
            try:
                tl_right_idx = bisect_right(tl_keys, self.current_way_point_index)
                next_reference_waypoint = tl_keys[tl_right_idx]
            except (ValueError, IndexError): # we have passed all traffic lights on our route
                tl_right_idx = None
                next_reference_waypoint = None
        
        if tl_right_idx == 0: # we have not passed any traffic light yet
            last_reference_waypoint = 0
        elif tl_right_idx is None:
            last_reference_waypoint = None
        else:
            try:
                last_reference_waypoint = tl_keys[tl_right_idx - 1]
            except (ValueError, IndexError, TypeError): 
                last_reference_waypoint = None
            
        if (last_reference_waypoint is not None) and (next_reference_waypoint is not None):
            distance = next_reference_waypoint - last_reference_waypoint
            progress = self.current_way_point_index - last_reference_waypoint
            if distance != 0: # measured in waypoints
                rel_progress = round(progress / distance, 2)
            else:
                rel_progress = 1 # no distance -> we are at the location we are heading for
        else: 
            rel_progress = 0 # at least one of the reference points cannot be determined
        return rel_progress

    def update_route(self, position:Position):
        """
        Determines 'current', 'next' and 'remaining' attributes based on current position.
        Checks if position is still in tolerance of the route. If not, issues
        creation of new route from current location to destination. Change 
        tolerance? Adjust 'route_deviation_tolerance'.
        """

        assert(self.start_navigating == True)

        self.current_position = position
        if self.is_on_route(position) == False:
            lat, lon = position.get_pos()
            departure = [lat, lon][::-1]
            #print(departure)
            logging.info(f"creating new route, \n\tstarting at {departure},\n\tdestination: {self.destination}")
            self.create_route(departure, destination=self.destination)
            self.start_navigating = True
        
        # determine way_point index
        self.current_way_point_index = self._get_current_waypoint_index()
        assert(self.current_way_point_index is not None)
        
        # determine navigation instructions
        cur_nav_instr_key = self._get_current_navigation_instruction_key()
        (self.current_nav_instr_text, 
         self.current_nav_instr_picture, 
         distance, 
         duration, 
         num_points) = (
             self.load_navigation_instruction(cur_nav_instr_key)
             )
        
        # distance to next direction
        self.remaining_distance = round((self.distance_integral[cur_nav_instr_key-1] 
                                        - self.distance_integral[self.current_way_point_index]))

        # update instruction list
        remaining_nav_instr_texts = []
        remaining_nav_instr_distances = []
        relevant = False
        for key, step in self.navigation_instructions.items():
            if key == cur_nav_instr_key:
                relevant = True
                remaining_nav_instr_texts.append(step["instruction"])
                remaining_nav_instr_distances.append(self.remaining_distance)
            elif relevant == True:
                remaining_nav_instr_texts.append(step["instruction"])
                remaining_nav_instr_distances.append(round(step["distance"]))
        self.remaining_nav_instr_texts = remaining_nav_instr_texts
        self.remaining_nav_instr_distances = remaining_nav_instr_distances

        # determine current speed limit
        self.current_speed_limit = self._get_current_speed_limit()

        # determine next two trafficlights next_tl and next_next_tl
        self.next_tl, self.next_next_tl = self._get_impending_two_trafficlights()
        if self.next_tl is not None:
            self._update_trafficlight(self.next_tl)
        else:
            self._update_recommended_speed(color=None, speed=0)
            self.status_next_tl = ""

        # progress-bar. 
        self.current_progress_next_tl = self._update_status_bar()       

    def get_all_trafficlight_coordinates(self):
        """use to plot trafficlights on map"""
        trafficlight_positions = list(self.trafficlights.items())
        return [list(self.way_points[point]) for point,_ in trafficlight_positions]
            
    def demo_n_clicks(self, nclicks):
        """
        Use on demo page only!
        Represents how many clicks have been made on the next-button representing the progress along the route.
        """
        try:
            lat, lon = self.way_points[nclicks-1]
        except (ValueError, IndexError):
            lat, lon = self.way_points[0]
        self.current_position.set_pos(lat, lon)
        self.update_route(self.current_position)
        return lat, lon
    
    def update_bicycle_mode(self, bicycle_mode:bool):
        self.bicycle_mode = bicycle_mode
        





        

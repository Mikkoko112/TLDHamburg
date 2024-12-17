import requests
import json
from pathlib import Path
from tldhamburg.frontend.position import Position
from tldhamburg.frontend.Trafficlights import Trafficlight
from tldhamburg.control.control import RoutePlanner
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from bisect import bisect_left, bisect_right

class Navigation:
    """
    documentation

    directions are the navigation instructions e.g. when and where to turn left
    """
    _path = None
    _route = None            # of class Route
    departure = None
    destination = None
    start_navigating = False
    route_deviation_tolerance = 100

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
    next_next_tl = None
        
    def __init__(self):
        self._path = f"{Path.cwd()}/schnittstelle"
    
    def create_route(self, departure:list, destination:list):
        # instruct creation of route
        self.departure = departure
        self.destination = destination
        nav_coordinates = {"coordinates": [departure,destination]}
        self._route = RoutePlanner(self._path)
        self._route.generateRoute(nav_coordinates)

        # route is saved as a geojson file. Load it...
        self.geojson = self._init_route_geojson()

        # build static data of the route
        self.navigation_instructions = self._init_navigation_instructions()
        self.way_points, self.way_points_lon_lat = self._init_waypoints()
        try:
            self.speed_limits = self._init_speed_limits()
        except (KeyError):
            self.speed_limits = None
        try:
            self.trafficlights = self._init_traffic_lights()
        except (KeyError):
            self.trafficlights = None
        
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
        

    # TODO ausbauen
    def __get_ors_route(self, api_key, departure, destination, profile='driving-car'):
        UPLOAD_DIRECTORY = f"{Path.cwd().parent}/schnittstelle"
        print(UPLOAD_DIRECTORY)
        url = f"https://api.openrouteservice.org/v2/directions/{profile}/geojson"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "language": "de",
            "coordinates": [
                departure,  # [longitude_start, latitude_start]
                destination     # [longitude_end, latitude_end]
            ],
            "format": "geojson"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            geojson_data = response.json()

            # Save to a .geojson file (optional)
            with open(f"{UPLOAD_DIRECTORY}/route.geojson", "w") as file:
                json.dump(geojson_data, file, indent=4)

            return geojson_data

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return None
    
    # TODO check loading of geojson works
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
                        8: "straight.png", 9: "U_turn.png", 10: "goal.png", 
                        11: "straight.png", 12: "keep_left.png" , 13: "keep_right.png"}
        dic_roundabouts = {1: "roundabout_right.png", 2: "roundabout_straight.png", 
                        3: "roundabout_left.png"}
        
        navigation_instructions = {}
        total_distance = 0
        total_duration = 0
        distance_integral = []
        duration_integral = []
        # TODO change back to 'steps' 
        steps = route["features"][0]["properties"]["segments"]["stepts"]
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
            
            # assuming approx. equal distance between waypoints of given step
            if num_waypoints == 0:
                distance_per_waypoint = 0
                duration_per_waypoint = 0
            else:
                distance_per_waypoint = step["distance"] / num_waypoints
                duration_per_waypoint = step["duration"] / num_waypoints
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

        # print(f"len waypoints = {len(self.way_points)}")
        # print(f"len integral = {len(distance_integral)}")
        # if len(self.way_points) == len(distance_integral):
        self.distance_integral = distance_integral
        self.duration_integral = duration_integral
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

    # TODO ausbauen ? Nike fragen
    def ausbauen_init_traffic_lights(self):
        route = self.geojson
        # Prepare Overpass API query
        overpass_url = "http://overpass-api.de/api/interpreter"
        steps = route["features"][0]["properties"]["segments"][0]["steps"]
        step_waypoints = [
        step["way_points"][1] for step in steps  
        ]
        step_coord = [
        [route['features'][0]['geometry']['coordinates'][i-1][1],route['features'][0]['geometry']['coordinates'][i-1][0]] for i in step_waypoints 
        ]
        #every_waypoints = route['features'][0]['geometry']['coordinates']
        #every_coord = [   point for point in every_waypoints]
        overpass_queries = []
        for lon, lat in step_coord: #step_coord
            overpass_queries.append(
                f"node[highway=traffic_signals](around:10,{lon},{lat});"
            )
        
        # Combine all queries into one Overpass query
        combined_query = "[out:json];(" + " ".join(overpass_queries) + ");out;"
        '''
        combined_query = f"""
        [out:json];
        (node
            [highway=traffic_signals]
            (around:100,{route['features'][0]['geometry']['coordinates'][0][1]},{route['features'][0]['geometry']['coordinates'][0][0]});
        node
            [highway=traffic_signals]
            (around:100,{route['features'][0]['geometry']['coordinates'][216][1]},{route['features'][0]['geometry']['coordinates'][216][0]});
        );
        out;
        """
        '''

        try:
            response = requests.get(overpass_url, params={'data': combined_query})
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()     

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return None  
        
    def is_on_route(self, current_position:Position):
        """
        Check if the current position is on or near the route.
        in: position(lat,lon)
        out: bool(on_route)
        Adjust tolerance in settings 'route_deviation_tolerance'
        """
        lat, lon = current_position.get_pos()
        point = Point(lat, lon)  # takes (lat, lon)
        route = LineString(self.way_points) # takes (lon, lat)
        nearest_point_on_route = nearest_points(route, point)[0]
        distance = point.distance(nearest_point_on_route)
        on_route = distance <= self.route_deviation_tolerance
        if on_route == False:
            print(f"distance to route: {distance}, tolerance: {self.route_deviation_tolerance}\ncurrent Position: {lat, lon}\nnearest point: {nearest_point_on_route}")

        return on_route
    
    def _get_current_waypoint_index(self):
        lat, lon = self.current_position.get_pos()
        point = Point(lat, lon)
        route = LineString(self.way_points)
        nearest_way_point = nearest_points(route, point)[0]
        for i, (lat, lon) in enumerate(self.way_points):
            if Point(lat, lon) == nearest_way_point:
                return i
        return None

    def _get_current_navigation_instruction_key(self):
        """
        determines upcoming navigation instruction key
        based on the current waypoint index
        """
        keys_list = sorted(self.navigation_instructions.keys())
        idx = bisect_right(keys_list, self.current_way_point_index)
        key = keys_list[idx]
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
            keys_list = sorted(self.speed_limits.keys())
            idx = bisect_right(keys_list, self.current_way_point_index)
            key = keys_list[idx]
            return self.speed_limits[key]
        else:
            return -1

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
        
    # TODO
    def _update_trafficlight(self, trafficlight:Trafficlight):
        status, nextPhase, nextPhaseTime, rapidUpdate, speed = (        
            self._route.getUpdateOnTrafficLight(trafficlight.things_id, """self.current_way_point_index"""))
        print(f"status = {status}")
        print(f"nextPhase = {nextPhase}")
        print(f"nextPhaseTime = {nextPhaseTime}")
        print(f"rapidUpdate = {rapidUpdate}")
        print(f"speed = {speed}")
        pass

    def start_navigation(self, position:Position):
        """
        toggles navigation to start if sensible
        requires position to be within 'route_deviation_tolerance'
        """
        if self.start_navigating == True:
            pass
        if self.is_on_route(position) == False:
            raise Exception("To start navigating, please come near the route")
        else:
            self.start_navigating = True
            self.update_route(position)
        
    def update_route(self, position:Position):
        """
        Determines 'current' and 'next' attributes based on current position.
        Checks if position is still in tolerance of the route. If not, issues
        creation of new route from current location to destination. Change 
        tolerance? Adjust 'route_deviation_tolerance'.
        """

        assert(self.start_navigating == True)

        self.current_position = position
        if self.is_on_route(position) == False:
            lat, lon = position.get_pos()
            departure = [lat, lon]
            self.create_route(departure, destination=self.destination)
            self.start_navigating = True
        
        # determine way_point index
        self.current_way_point_index = self._get_current_waypoint_index()

        # determine navigation instructions
        cur_nav_instr_key = self._get_current_navigation_instruction_key()
        (self.current_nav_instr_text, 
         self.current_nav_instr_picture, 
         distance, 
         duration, 
         num_points) = (
             self.load_navigation_instruction(cur_nav_instr_key)
             )
        
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
                remaining_nav_instr_distances.append(step["distance"])
        self.remaining_nav_instr_texts = remaining_nav_instr_texts
        self.remaining_nav_instr_distances = remaining_nav_instr_distances


        # determine next two trafficlights next_tl and next_next_tl
        self.next_tl, self.next_next_tl = self._get_impending_two_trafficlights()

        # determine current speed limit
        self.current_speed_limit = self._get_current_speed_limit()

        # distance to next direction
        self.remaining_distance = (self.distance_integral[cur_nav_instr_key-1] 
                                        - self.distance_integral[self.current_way_point_index])

        # progress-bar. 
        tl_keys = list(self.trafficlights.keys())
        try:
            tl_right_idx = bisect_right(tl_keys, self.current_way_point_index)
            next_reference_waypoint = tl_keys[tl_right_idx]
        except (ValueError, IndexError):
            next_reference_waypoint = 0
        try:
            tl_left_idx = bisect_left(tl_keys, self.current_way_point_index)
            last_reference_waypoint = tl_keys[tl_left_idx]
        except (ValueError, IndexError): 
            last_reference_waypoint = 0 
        num_waypoints = next_reference_waypoint - last_reference_waypoint + 1
        progress = self.current_way_point_index - last_reference_waypoint
        if num_waypoints <= 0:
            rel_progress = 1
        else:
            rel_progress = round(progress / num_waypoints, 2)
        self.current_progress_next_tl = rel_progress
    
    def get_all_trafficlight_coordinates(self):
        trafficlight_positions = list(self.trafficlights.items())
        return [self.way_points[point] for point in trafficlight_positions]
            

    def demo_n_clicks(self, nclicks):
        """use on demo page only"""
        try:
            lat, lon = self.way_points[nclicks-1]
        except (ValueError, IndexError):
            lat, lon = self.way_points[0]
        self.update_route(self.current_position.set_pos(lat, lon))
        return lat, lon
        





        

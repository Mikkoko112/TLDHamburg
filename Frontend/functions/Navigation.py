import requests
import json
from pathlib import Path
import APIkeys
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
import settings

class Navigation:
    departure = None
    destination = None
    route_type = None
    _profile = None         # ORS: “driving-car”, “driving-hgv”, “foot-walking”, “foot-hiking”, “cycling-regular”, “cycling-road”,”cycling-mountain”, “cycling-electric”
    geojson = None          # actual content of geojson file
    directions = None       # navigation instructions
    dir_pictures = None     # display pictures matching instruction of given index
    way_points = []         # list of coordinates representing the route
    dir2wp = None           # maps directions -> way_points; start_idx, end_idx = dir2wp[dir_idx]
    wp2dir = None           # maps way_point -> directions; dir = wp2dir[wp_idx]
    current_way_point = None # idx of way point
    current_direction = None
    current_dir_picture = None
    current_progress = None # progress to next traffic light
    next_tl = None          # Trafficlight Object
    next_next_tl = None
        
    def __init__(self, route_type="ORS"):
        if route_type == "ORS":
            self.route_type = route_type
        pass
    
    def create_route(self, departure, destination, profile='driving-car'):
        self.departure = departure
        self.destination = destination
        self._profile = profile
        if self.route_type == "ORS":
            api_key = APIkeys.ORS_key
            self.__get_ors_route(api_key, departure, destination)
        self.geojson = self.get_route_geojson()
        self.dir_pictures, self.directions = self.__get_directions()
        self.way_points = self.__get_waypoints()
        self.dir2wp, self.wp2dir = self.__get_direction_of_waypoint()

    def __get_direction_of_waypoint(self):
        """ creates mapping lists: 
        directions -> way_points, way_point -> directions
        wp2dir_list[idx_of_way_point] will return number of current direction instruction"""
        dir2wp_list = []
        for i in range(len(self.geojson["features"][0]["properties"]["segments"][0]["steps"])):
            dir2wp_list.append(self.geojson["features"][0]["properties"]["segments"][0]["steps"][i]["way_points"])
        wp2dir_list = list()
        for dir in range(len(dir2wp_list)): # for every direction instruction
                wp2dir_list.append([dir]*(dir2wp_list[dir][1]-dir2wp_list[dir][0])) # add an entry for each relevant way_point
        return dir2wp_list, wp2dir_list

    def __get_ors_route(self, api_key, departure, destination, profile='driving-car'):
        cwd = Path.cwd()
        UPLOAD_DIRECTORY = f"{cwd}/schnittstelle"
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
        
    def get_route_geojson(self):
        cwd = Path.cwd()
        directory = f"{cwd}/schnittstelle"
        with open(f"{directory}/route.geojson", "r") as f:
            route_geojson = json.load(f)
        return route_geojson

    def __get_directions(self):
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
        route_pictures = []
        route_instructions = []

        steps = route["features"][0]["properties"]["segments"][0]["steps"]
        for step in steps:
            val = dic_directions[step["type"]]
            if val == "Enter roundabout":
                val = dic_roundabouts[step["exit_number"]]
            route_pictures.append(val)
            route_instructions.append(step["instruction"])
        return route_pictures, route_instructions
    
    def __get_waypoints(self):
        return self.geojson['features'][0]['geometry']['coordinates']
    
    def __get_traffic_lights(self):
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
        
    def is_on_route(self, current_position, way_points): 
        # Check if the current position is on or near the route.
        # current_position = [lat, lon]
        # way_points = [[lon, lat], [lon, lat], ...]

        point = Point(current_position[0], current_position[1])  # takes (lat, lon)
        route = LineString(way_points) # takes (lon, lat)

        distance = point.distance(route)
        on_route = distance <= settings.route_deviation_tolerance
        
        if on_route == False:
            self.create_route(current_position, self.destination)

        return on_route
    
    def update_route(self, current_position):
        # determines 'current' and 'next' attributes based on current position

        # determine way_point index
        pos = Point(current_position[0], current_position[1])
        route = LineString(self.way_points)
        nearest_way_point = nearest_points(route, pos)[0]
        self.current_way_point = self.way_points.index(nearest_way_point)

        # determine direction instructions
        self.wp2dir[self.current_way_point]
        self.current_dir_picture[self.current_way_point]

        # distance to next direction
        # from geopy.distance import geodesic
        # self.next_direction_distance = distance(start, end)

        # determine progress to next trafficlight (progress-bar)
        # section_start = Point(lat, lon)
        # section_end = Point(lat, lon)



        

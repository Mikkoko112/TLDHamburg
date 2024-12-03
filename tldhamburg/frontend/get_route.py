import requests
import json
from pathlib import Path
#from PIL import Image

# löschen!!!!

class Route:
    _json = None
    '''def __init__(self):
        cwd = Path.cwd()
        directory = f"{cwd}/schnittstelle"
        with open(f"{directory}/route2.geojson", "r") as f:
            self._json = json.load(f)
    '''
    def __init__(self, api_key, start_coords, end_coords, profile='driving-car'):
        UPLOAD_DIRECTORY = f"{Path.cwd()}/Frontend/schnittstelle"
        url = f"https://api.openrouteservice.org/v2/directions/{profile}/geojson"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "language": "de",
            "coordinates": [
                start_coords,  # [longitude_start, latitude_start]
                end_coords     # [longitude_end, latitude_end]
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
                
            self._json = geojson_data
            
        except requests.exceptions.RequestException as e:
            print("Error:", e)
    
        
    def load_route(self):
        return self._json 

    def get_directions(self):
        #path = f"{Path.cwd().parent}/assets/"
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

        steps = self._json["features"][0]["properties"]["segments"][0]["steps"]
        for step in steps:
            val = dic_directions[step["type"]]
            if val == "Enter roundabout":
                val = dic_roundabouts[step["exit_number"]]
            route_pictures.append(val)
            route_instructions.append(step["instruction"])
        return route_pictures, route_instructions
    
    def get_waypoints(self):
        waypoints = self._json["features"][0]["geometry"]["coordinates"]
        return waypoints
    '''
    Output: [[9.931935, 53.597643], [9.932123, 53.597574], [9.932212, 53.597529], [9.932338, 53.597414], [9.932695, 53.596923], [9.932818, 53.596841], [9.93352, 53.596908], [9.93375, 53.596935], [9.933908, 53.596985], [9.934158, 53.59713], [9.93432, 53.597276], [9.934514, 53.597415], [9.935048, 53.597701], [9.935504, 53.597876], [9.936006, 53.598011], [9.936291, 53.598086], [9.936709, 53.598196], [9.936759, 53.598209], [9.938003, 53.598547], [9.938742, 53.59875], [9.939109, 53.598829], [9.940228, 53.598955], [9.941057, 53.599043], [9.941683, 53.599108], [9.941745, 53.599043], [9.941866, 53.59902], [9.941984, 53.599059], [9.942018, 53.599136], [9.943195, 53.599252], [9.94385, 53.599316], [9.944384, 53.599345], [9.94517, 53.599336], [9.945657, 53.5993], [9.947193, 53.599095], [9.947364, 53.599084], [9.947655, 53.59908], [9.947896, 53.59909], [9.948303, 53.599134], [9.950342, 53.599491], [9.950885, 53.59955], [9.951439, 53.5995], [9.951724, 53.599512], [9.951868, 53.599304], [9.952188, 53.598884], [9.95232, 53.598786], [9.952469, 53.598734], [9.952615, 53.598715], [9.953237, 53.598786], [9.956268, 53.599036], [9.95766, 53.5991], [9.958526, 53.599118], [9.958687, 53.599118], [9.9591, 53.59914], [9.959553, 53.599204], [9.960516, 53.599351], [9.960938, 53.599419], [9.961791, 53.599545], [9.962163, 53.599585], [9.962984, 53.599679], [9.963526, 53.599751], [9.9639, 53.599762], [9.964364, 53.599337], [9.965076, 53.598644], [9.965167, 53.598519], [9.965316, 53.598209], [9.965502, 53.597809], [9.965909, 53.59679], [9.96611, 53.596092], [9.966232, 53.595554], [9.966433, 53.594516], [9.966535, 53.594023], [9.966563, 53.593892], [9.966582, 53.593809], [9.966708, 53.593285], [9.967018, 53.592115], [9.967321, 53.590977], [9.96733, 53.590944], [9.967479, 53.590523], [9.967576, 53.590089], [9.96771, 53.589257], [9.967753, 53.588999], [9.967824, 53.588571], [9.968208, 53.586913], [9.968424, 53.586312], [9.968461, 53.586209], [9.968479, 53.586158], [9.968502, 53.586096], [9.968563, 53.585922], [9.968631, 53.585615], [9.96875, 53.585243], [9.968869, 53.584953], [9.969089, 53.5846], [9.969113, 53.584562], [9.969265, 53.584355], [9.96944, 53.58413], [9.969539, 53.584006], [9.969651, 53.583863], [9.97018, 53.583364], [9.97038, 53.583197], [9.970571, 53.583023], [9.97076, 53.58285], [9.971279, 53.582377], [9.97165, 53.582055], [9.971826, 53.581926], [9.971975, 53.581818], [9.9732, 53.580756], [9.975189, 53.579007], [9.975291, 53.578908], [9.975379, 53.578824], [9.975663, 53.578579], [9.975721, 53.578535], [9.976062, 53.57828], [9.976323, 53.57814], [9.976671, 53.577963], [9.976789, 53.577901], [9.976934, 53.577812], [9.977444, 53.57738], [9.97754, 53.577296], [9.977679, 53.577174], [9.977834, 53.577], [9.977896, 53.576906], [9.97794, 53.576757], [9.977926, 53.576512], [9.977783, 53.576142], [9.977623, 53.57573], [9.977451, 53.575261], [9.977325, 53.574705], [9.977304, 53.574504], [9.977341, 53.574282], [9.977539, 53.57375], [9.977773, 53.573335], [9.977884, 53.573164], [9.978206, 53.57275], [9.978476, 53.572311], [9.978306, 53.572235], [9.978352, 53.572072], [9.978398, 53.571911], [9.978375, 53.57157], [9.978382, 53.571099], [9.978406, 53.570946], [9.978474, 53.570727], [9.978573, 53.570512], [9.978954, 53.569845], [9.979096, 53.569622], [9.980065, 53.568207], [9.980659, 53.567294], [9.980791, 53.567126], [9.9809, 53.566997], [9.980961, 53.566941], [9.981593, 53.566404], [9.981992, 53.566074], [9.982443, 53.565711], [9.982812, 53.565413], [9.983187, 53.5651], [9.983531, 53.56482], [9.983703, 53.564678], [9.984148, 53.564316], [9.984362, 53.56411], [9.984486, 53.564015], [9.984686, 53.563881], [9.985557, 53.563537], [9.988573, 53.561998], [9.989487, 53.561528], [9.989562, 53.561474], [9.989864, 53.56121], [9.990329, 53.560797], [9.990521, 53.560603], [9.990568, 53.560534], [9.990611, 53.560479], [9.990664, 53.560422], [9.990758, 53.560322], [9.991198, 53.559824], [9.99149, 53.559571], [9.991718, 53.559407], [9.991966, 53.559259], [9.992366, 53.559063], [9.993576, 53.558669], [9.993771, 53.558624], [9.994205, 53.558544], [9.994533, 53.558513], [9.994989, 53.558466], [9.995251, 53.558459], [9.996764, 53.558058], [9.997405, 53.557876], [9.998481, 53.557592], [9.99889, 53.557483], [9.999465, 53.55736], [9.999811, 53.557306], [10.000359, 53.557283], [10.000877, 53.557285], [10.001087, 53.557287], [10.001778, 53.557193], [10.00208, 53.557131], [10.002229, 53.557072], [10.002609, 53.556915], [10.002823, 53.556892], [10.002941, 53.556905], [10.003764, 53.557233], [10.003924, 53.557306], [10.004993, 53.557646], [10.005098, 53.55766], [10.005217, 53.557646], [10.006401, 53.55705], [10.006799, 53.556807], [10.006837, 53.556716], [10.006772, 53.556666], [10.006362, 53.556434], [10.007391, 53.555928], [10.0076, 53.555852], [10.007764, 53.555383], [10.007847, 53.555319], [10.007829, 53.55522], [10.007916, 53.55499], [10.007973, 53.55487], [10.008341, 53.55364], [10.008677, 53.552497], [10.008642, 53.552401], [10.008591, 53.552349]]
    '''

    def get_step_waypoints(self):
        steps = self._json["features"][0]["properties"]["segments"][0]["steps"]
        step_waypoints = [
        step["way_points"][1] for step in steps  
        ]
        step_waypoints.insert(0,0)
        return step_waypoints
    '''
    Output: step_waypoints = [0, 5, 23, 41, 44, 60, 131, 133, 134, 198, 201, 206, 208, 215, 217, 217]
    '''

    def get_trafficlight_ids(self):
        all_tl = self._json["features"][0]["properties"]["trafficlights"]["features"]
        tl_ids = [tl["properties"]["id"] for tl in all_tl]
        return tl_ids
    
    def get_traffic_lights(self):
        # Prepare Overpass API query
        overpass_url = "http://overpass-api.de/api/interpreter"
        steps = self._json["features"][0]["properties"]["segments"][0]["steps"]
        step_waypoints = [
        step["way_points"][1] for step in steps  
        ]
        step_coord = [
        [self._json['features'][0]['geometry']['coordinates'][i-1][1],self._json['features'][0]['geometry']['coordinates'][i-1][0]] for i in step_waypoints 
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
            step_waypoints.insert(0,0)
            return response.json()     

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return None  

    


'''
# Example usage
if __name__ == "__main__":
    api_key = "YOUR_API"  # Replace with your actual API key
    start_coords = [13.4050, 52.5200]  # Berlin (longitude, latitude)
    end_coords = [9.9937, 53.5511]     # Hamburg (longitude, latitude)

    directions = get_route(api_key, start_coords, end_coords)
    if directions:
        print(json.dumps(directions, indent=4))  # Print the GeoJSON response
'''
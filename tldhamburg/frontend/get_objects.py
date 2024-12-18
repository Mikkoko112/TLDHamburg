import dash_leaflet as dl
import base64
from tldhamburg.backend.Things import Things

# Function to generate Leaflet Markers based on the status of traffic lights
def get_trafficlights(lights):
    traffic_light_markers = [
        dl.Marker(
        position=[lat, lon],
        children=[dl.Tooltip("Traffic Light")]
        ) for lon,lat in lights 
        ]
    return traffic_light_markers
    '''
    for light in lights:
        # Change marker color based on traffic light status
        color = {"red": "red", "green": "green", "yellow": "orange"}[light['status']]
        light = dl.Marker(position=[light['lat'], light['lon']], children=[
            dl.Tooltip(f"Traffic Light {light['id']}: {light['status'].capitalize()}"),
            # dl.CircleMarker(center=[light['lat'], light['lon']], color=color, radius=10),
            dl.Circle(center=[light['lat'], light['lon']], radius=5)
        ])
        markers.append(light)
    return markers
'''

def get_marker(dep_dest):
    """
    Sets navigation departure and destination marker

    Parameters:
    list(dep_dest{'id': str, 'lat': float, 'lon': float}): list of start and end coordinates    
    
    Returns: Dash-Leaflet marker

    Example Input
    positions = [{"id": "start", "lat": 53.5975929, "lon": 9.9318831},
               {"id": "end", "lat": 53.5524079, "lon": 10.0084222}]
    """    
    out = []
    for pos in dep_dest:
        marker = dl.Marker(position=[pos['lat'], pos['lon']],
                children=[
                    dl.Tooltip(f"{pos['id']}"),
                ])
        out.append(marker)
    return out
'''
def get_marker_id(ids_list):
    # {2: [[[9.9196439, 53.5638321], [9.9197085, 53.5637359], [9.9198219, 53.5635865], [9.9198451, 53.5635559], [9.9198231, 53.5634831], [9.9198481, 53.563453]], [[9.9197087, 53.563736], [9.9195566, 53.5639624], [9.9195566, 53.5639624], [9.919899, 53.5639529]], [[9.9197629, 53.5639568], [9.9198989, 53.5639531], [9.9200006, 53.5639497]]]}
    things = Things(ids_list)
    observations = things.get_primary_signal_observations(ids_list, n_obsrvtns=1, phnTime=True)
    coordinations = things.get_coordinates()
    markers = []
    color_mapping = {0: "black", 1: "red", 2: "yellow", 3: "green", 4: "orange", 5: "orange", 6: "green", 9: "white"}
    for id, pos_groups in coordinations.items():
        for pos_group in pos_groups:
            for pos in pos_group:
                color = color_mapping.get(observations[id][0][1])  # (observations[id][0][1], "black") Default to black for safety
                marker = dl.CircleMarker(center=[pos[1],pos[0]], color=color, radius=10
                                    #children = [
                                        #dl.Tooltip(f"{id}: {pos[1]} {pos[0]}"),
                                    #    dl.CircleMarker(center=[pos[1], pos[0]], ),
                                    #]
                                    )
                markers.append(marker)
    return markers
'''
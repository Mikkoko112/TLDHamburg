import dash_leaflet as dl

def get_trafficlights(lights):
    """
    Sets traffic light markers.

    Parameters:
    list(list(lon.float,lat.float), list(lon.float,lat.float), ....): list of the traffic lights   
    
    Returns: Dash-Leaflet markers

    Example Input
    lights = [[9.90627193450928, 53.5681304931641], [9.90691184997559, 53.5672760009766]]
    """    
    traffic_light_markers = [
        dl.Marker(
        position=[lat, lon],
        children=[dl.Tooltip("Traffic Light")]
        ) for lon,lat in lights 
        ]
    return traffic_light_markers

def get_marker(dep_dest):
    """
    Sets navigation departure and destination marker.

    Parameters:
    list(dep_dest{'id': str, 'lat': float, 'lon': float}): list of start and end coordinates    
    
    Returns: Dash-Leaflet marker

    Example Input
    positions = [{"id": "departure", "lat": 53.5975929, "lon": 9.9318831, "icon": dl.Icon(color='red')},
               {"id": "destination", "lat": 53.5524079, "lon": 10.0084222, "icon": dl.Icon(color='white')}]
    """    
    out = []
    for i,pos in enumerate(dep_dest):
        if i == 0:
            marker = dl.CircleMarker(center=[pos['lat'], pos['lon']], radius=10,color="blue",
                children=[
                    dl.Tooltip(f"{pos['id']}"),
                ])
        elif i == 1:
            marker = dl.CircleMarker(center=[pos['lat'], pos['lon']],radius=10,color="black",
                children=[
                    dl.Tooltip(f"{pos['id']}"),
                ]) 
        out.append(marker)
    return out

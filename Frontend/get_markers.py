import dash_leaflet as dl

# Function to generate Leaflet Markers based on the status of traffic lights
def get_markers(lights):
    markers = []
    for light in lights:
        # Change marker color based on traffic light status
        color = {"red": "red", "green": "green", "yellow": "orange"}[light['status']]
        marker = dl.Marker(position=[light['lat'], light['lon']], children=[
            dl.Tooltip(f"Traffic Light {light['id']}: {light['status'].capitalize()}"),
            dl.CircleMarker(center=[light['lat'], light['lon']], color=color, radius=10)
        ])
        markers.append(marker)
    return markers
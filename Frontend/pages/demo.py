#from threading import Timer
#from pathlib import Path

import dash
from dash import dcc, html, no_update, ctx, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import dash_bootstrap_components as dbc

from tldhamburg.frontend import APIkeys
from tldhamburg.frontend import * # in __innit__.py __all__ = ["filename.py", "otherfile.py",...]

# import components of the page
from .components import navbar_demo
from .components import data_demo


dash.register_page(__name__,
                    path='/demo',
                    title='Demo: Traffic-Light Navigation',
                    name='Demo: Traffic-Light Navigation')

#external CSS stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

ORS_key = APIkeys.ORS_key 

# Initial markers locations and statuses
#marker_1 = [{"id": "start", "lat": 53.5533, "lon": 10}, {"id": "end", "lat": 53.5, "lon": 10}]
 
#current_pos = [{"id": "current_pos", "lat": None, "lon": None}]

#traffic_lights = [
#     {"id": 1, "lat": None, "lon": None, "status": "red"},
#     {"id": 2, "lat": None, "lon": None, "status": "green"}
#     ]

#marker_url = app.get_asset_url("location_on.png")
# lat: latitude (Breite)
# lon: longitude (Länge

current_speed = "-"
necessary_speed = 29

# it will show the map with the markers and the Overview
#geojson = 1
position = position.Position() # Create a position Object

# Main layout
def layout(**kwargs): 
    return dbc.Container(children = [
    navbar_demo(),
    data_demo(position,current_speed,necessary_speed)
    ],
    fluid = True, # remove the margins
    style={"padding": 0,
           "height": "98vh",
           "width": "100%"}, # removes ALL the margins
    className="bg-light", # background color
)

# triggers if you click the button
# this callback will get the Input for the start and end adresses
# it will give back the coordinates and shows them in the map as a marker
# it also generates a route and show it in the map
@callback(
    Output(component_id="startpunkt", component_property="valid"), 
    Output("startpunkt", "invalid"),
    Output(component_id="endpunkt", component_property="valid"), 
    Output("endpunkt", "invalid"),
    Output("route_button", "n_clicks"),
    #Output("coordinates_start", "children"),
    #Output("coordinates_end", "children"),
    Output("start-end-layer", "children"),
    Output("route-layer", "data"),
    Output("tf-route-layer", "children"),
    Output("start_next_button", "disabled"),
    #Output("position", "center"),
    [State("startpunkt","value"),
     State("endpunkt","value"),
     Input("route_button", "n_clicks"),
     ],
     running=[
        (Output("route_button", "disabled"), True, False),
    ],
    prevent_initial_call=True
)
def check_validity(starttext, endtext, n_clicks): 
    marker = [{"id": "departure", "lat": 53.5975929, "lon": 9.9318831},
                  {"id": "destination", "lat": 53.5524079, "lon": 10.0084222}]
    if n_clicks:
        if starttext or endtext: 
            is_valid_start = True
            is_valid_end = True
            start_lat, start_lon = geocoding_utils.return_coordinates(starttext)
            end_lat, end_lon = geocoding_utils.return_coordinates(endtext)
            if start_lat == None:
                is_valid_start = False
            else:
                marker[0].update({"lat": start_lat, "lon": start_lon})
            if end_lat == None:
                is_valid_end = False
            else:
                marker[1].update({"lat": end_lat, "lon": end_lon})
            #get route
            route = get_route.Route(ORS_key, [start_lon,start_lat], [end_lon, end_lat])
            position.set_pos(lat=start_lat, lon=start_lon)

            #global variables for instructions and waypoints
            global route_pictures, route_instructions, waypoints, step_waypoints 
            route_pictures, route_instructions = route.get_directions()
            waypoints = route.get_waypoints()
            #get traffic lights and step waypoints
            step_waypoints = route.get_step_waypoints()
            traffic_light_response = route.get_traffic_lights() #traffic_light_response = route.get_trafficlight_ids() 
            return (is_valid_start, 
                    not is_valid_start, 
                    is_valid_end, 
                    not is_valid_end, 
                    0, 
                    #f"{start_lat}\t{start_lon}", 
                    #f"{end_lat}\t{end_lon}", 
                    get_objects.get_marker(marker), 
                    route.load_route(), 
                    get_objects.get_trafficlights(traffic_light_response),  #get_objects.get_marker_id(traffic_light_response),
                    False)#, position.get_pos()
    return (False, False, False, False, 0, 
            #"", "", 
            no_update, no_update, no_update, no_update)#, no_update #no input yet
    #raise dash.exceptions.PreventUpdate

# stores the data of the View for the whole route 
# (important for the button "restart")
@callback(
    Output('map-store', 'data'),
    Input('route-layer', 'data'),
    State("map", "zoom"),
    State("map", "center")
)
def store_map_view(data, zoom, center):
    if data is not None:
        return {'center': center, 'zoom': zoom}
    return no_update


# go through the steps of the route with the start/next button
# progress shows in the progressbar
@callback(
    Output("start_next_button", "n_clicks"),
    Output("start_next_button", "children"),
    Output("route_picture", "src"),
    Output("route_instruction", "children"),
    Output('map', 'viewport'),
    Output("prev_button", "disabled"),
    Output("restart_button", "disabled"),
    Output("progress", "value"),
    Output("prev_button", "n_clicks"),

    Input("start_next_button", "n_clicks"),
    Input("prev_button", "n_clicks"),
    Input("restart_button", "n_clicks"),
    State("map-store", "data"),
    running=[
        (Output("start_next_button", "disabled"), True, False),
    ],
    prevent_initial_call=True
    #Output("position", "center"),
)
def show_instructions(n_clicks, prev, restart, store):
    button_id = ctx.triggered_id
    if button_id == "restart_button":
        return (0, "Start",
                "", 
                "",
                store,
                True, True, 0, 0)
    elif button_id == "prev_button":
        if prev == 1:
            global step_waypoints_rev 
            step_waypoints_rev = [x - 1 for x in step_waypoints]
        n_clicks = n_clicks-1
        if n_clicks-1 in step_waypoints_rev:
            value = (n_clicks/len(waypoints))*100
            index = step_waypoints_rev.index(n_clicks-1)  
            return (n_clicks, "Next",
                    dash.get_relative_path(f"/assets/{route_pictures[index-1]}"),
                    #app.app_get_asset_url(f"{Path.cwd().parent}/assets", route_pictures[index-1]), 
                    route_instructions[index-1],
                    dict(center=geocoding_utils.convert_to_lat_lon(waypoints[n_clicks-1]), zoom=18),
                    False, False, value, no_update
                    #position.get_pos()
                    )
    value = (n_clicks/len(waypoints))*100
    if n_clicks and route_pictures != []:
        if n_clicks == 1:
            return (n_clicks, "Next", 
                        dash.get_relative_path(f"/assets/{route_pictures[0]}"),
                        #app.app_get_asset_url(f"{Path.cwd().parent}/assets", route_pictures[0]), 
                        route_instructions[0],
                        dict(center=geocoding_utils.convert_to_lat_lon(waypoints[0]), zoom=18, transition = "setView"), #flyTo 
                        True,False, value, no_update
                        #position.get_pos()
                        ) 
        
        elif n_clicks == len(waypoints):
            #print(f"if nclicks == len: {waypoints[n_clicks-1]}")
            return (0, "Start", 
                    dash.get_relative_path(f"/assets/{route_pictures[-1]}"),
                    #app.app_get_asset_url(f"{Path.cwd().parent}/assets", route_pictures[-1]), 
                    route_instructions[-1], 
                    dict(center=geocoding_utils.convert_to_lat_lon(waypoints[-1]), zoom=18),
                    False, False, value, no_update
                    #position.get_pos()
                    )
        
        elif n_clicks-1 in step_waypoints:
            #print(f"if nclicks in stepway: {waypoints[n_clicks-1]}")
            index = step_waypoints.index(n_clicks-1)  
            return (n_clicks, "Next", 
                    dash.get_relative_path(f"/assets/{route_pictures[index]}"),
                    #app.app_get_asset_url(f"{Path.cwd().parent}/assets", route_pictures[index]), 
                    route_instructions[index],
                    dict(center=geocoding_utils.convert_to_lat_lon(waypoints[n_clicks-1]), zoom=18),
                    False, False, value, no_update
                    #position.get_pos()
                    )
        
        #print(f"if nclicks not in stepway: {waypoints[n_clicks-1]}")
        return (n_clicks, "Next", 
                no_update, 
                no_update, 
                dict(center=geocoding_utils.convert_to_lat_lon(waypoints[n_clicks-1]), zoom=18),
                False, False, value, no_update
                #position.get_pos()
                )

    return 0, "Start", "", "", dict(center=no_update, zoom=no_update), True, True, 0#, None

@callback(
    Output("tf_picture","src"),
    Input("tf_picture","src")
)
def tf_pic(src):
    if src == "":
        return dash.get_relative_path(f"/assets/tf_off.png")
    return no_update
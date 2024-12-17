#from threading import Timer
#from pathlib import Path

import dash
from dash import dcc, html, no_update, ctx, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import dash_bootstrap_components as dbc


import pandas as pd

from tldhamburg.frontend import APIkeys
from tldhamburg.frontend import * # in __innit__.py __all__ = ["filename.py", "otherfile.py",...]

from tldhamburg.frontend.Navigation import Navigation
from tldhamburg.frontend.position import Position

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

current_speed = "-"
necessary_speed = 29

# it will show the map with the markers and the Overview
pos = Position() # Create a Position object
navigate = Navigation() # Create a Navigation object

# Main layout
def layout(**kwargs): 
    return dbc.Container(children = [
    navbar_demo(),
    data_demo(pos)
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
    Output("startpunkt", "valid"),          # True: shows if the input (departure) is valid (green)
    Output("startpunkt", "invalid"),        # True: shows if the input (departure) is invalid (red)
    Output("endpunkt", "valid"),            # True: shows if the input (destination) is valid (green) 
    Output("endpunkt", "invalid"),          # True: shows if the input (destination) is invalid (red)
    Output("route_button", "n_clicks"),     # set n_clicks to 0 
    Output("start-end-layer", "children"),  # load star and end point into the map
    Output("route-layer", "data"),          # load route (geojson) into the map
    #Output("tl-route-layer", "children"),  # load traffic lights into the map
    Output("start_next_button", "disabled"),# True: disables the start/next button if no route is given
    #Output("position", "center"),          # shows the live position
    Output("tab-2","disabled"),             # enables the Overview tab
    Output("instruction-overview","children",allow_duplicate=True),  # list all instruction 

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
            # get the coordinates for the departure and destination
            start_lat, start_lon = geocoding_utils.return_coordinates(starttext)
            end_lat, end_lon = geocoding_utils.return_coordinates(endtext)
            # if no address under this name is found, set valid False
            if start_lat == None:
                is_valid_start = False
            else:
                marker[0].update({"lat": start_lat, "lon": start_lon})
            if end_lat == None:
                is_valid_end = False
            else:
                marker[1].update({"lat": end_lat, "lon": end_lon})
            
            if not is_valid_start or not is_valid_end :
                return (is_valid_start, 
                    not is_valid_start, 
                    is_valid_end, 
                    not is_valid_end, 
                    0, 
                    no_update, 
                    no_update, 
                    #get_objects.get_trafficlights(traffic_light_response),  #get_objects.get_marker_id(traffic_light_response),
                    no_update,
                    no_update,
                    no_update)#, position.get_pos()
            
            #get route from ORS 
            navigate.create_route([start_lon,start_lat], [end_lon, end_lat])
            pos.set_pos(lat=start_lat, lon=start_lon)

            #global variables for instructions and waypoints
            """global route_pictures, route_instructions, route_distances, route_durations, waypoints, step_waypoints
            route_pictures, route_instructions, route_distances, route_durations = route.get_directions()

            waypoints = route.get_waypoints()
            #get traffic lights and step waypoints
            step_waypoints = route.get_step_waypoints()
            # change to new function for tl from geojson #traffic_light_response = route.get_trafficlight_ids() 
            #traffic_light_response = route.get_traffic_lights()
            l = [0]
            l.extend(route_distances[:-1]) """
            return (is_valid_start, 
                    not is_valid_start, 
                    is_valid_end, 
                    not is_valid_end, 
                    0, 
                    get_objects.get_marker(marker), 
                    navigate.geojson, 
                    #get_objects.get_trafficlights(traffic_light_response),  #get_objects.get_marker_id(traffic_light_response),
                    False,
                    False,
                    (dbc.Table.from_dataframe(pd.DataFrame(
                        # TODO build lists...
                            {
                                "in ... metern": navigate.remaining_nav_instr_distances,
                                "Anweisung": navigate.remaining_nav_instr_texts,
                            }), striped=True, bordered=True, hover=True)),)#, position.get_pos()
    return (False, 
            False, 
            False, 
            False, 
            0, 
            no_update, 
            no_update, 
            #no_update, 
            no_update,
            no_update,
            no_update)#, no_update #no input yet


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
    Output("start_next_button", "n_clicks"),    # 
    Output("start_next_button", "children"),    # change text from start to next after going one step
    Output("route_picture", "src"),             # change picture for instruction
    Output("route_instruction", "children"),    # change text for instruction
    Output('map', 'viewport'),                  # change view of the map
    Output("prev_button", "disabled"),          # True: disables the prev button
    Output("restart_button", "disabled"),       # True: disables the restart button
    Output("progress", "value"),                # change progress value 
    Output("prev_button", "n_clicks"),          # 

    Output("instruction-overview","children"),  # list all instruction still left
    #Output("picture-overview", "src"),         # list all pictures for the instructions

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
    
    # return values
    button_text = "Start"
    picture = ""
    text = ""
    # store = dict(center=no_update, zoom=no_update)
    toggle_prev_button = True
    toggle_next_button = True
    progress_val = 0
    prev_nclicks = 0
    remaining_instructions = ""

    # restart the route instructions and picture
    if button_id == "restart_button":
        n_clicks = 0
        pos.set_pos(navigate.demo_n_clicks(n_clicks))
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                    # TODO see above
                    {
                        "in ... metern": navigate.remaining_nav_instr_distances,
                        "Anweisung": navigate.remaining_nav_instr_texts,
                    }), striped=True, bordered=True, hover=True))
    
    # go one step back
    elif button_id == "prev_button":
        n_clicks = n_clicks - 1
    pos.set_pos(navigate.demo_n_clicks(n_clicks))


    

        # if n_clicks-1 in step_waypoints_rev:
        #     value = navigate.current_progress_next_tl
            # index = step_waypoints_rev.index(n_clicks-1)  
            # return (n_clicks, "Next",
            #         dash.get_relative_path(f"/assets/{navigate.current_nav_instr_picture}"),
            #         f"In {route_distances[index-2]}m: {route_instructions[index-1]}",
            #         dict(center=geocoding_utils.convert_to_lat_lon(waypoints[n_clicks-1]), zoom=18),
            #         False, False, value, no_update,
            #         (dbc.Table.from_dataframe(pd.DataFrame(
            #         {
            #             "in ... metern": l[index-2:],
            #             "Anweisung": route_instructions[index-2:],
            #         }), striped=True, bordered=True, hover=True))
                    #""
                    #position.get_pos()
                    # )
    
    # calculate overall progress -> change later to progress to the next trafficlight
    value = navigate.current_progress_next_tl*100

    


    # go one step further
    if n_clicks and navigate.navigation_instructions != {}:
        # first step: change button Start to Next
        if n_clicks == 1:
            return (n_clicks, "Next", 
                        dash.get_relative_path(f"/assets/{navigate.current_nav_instr_picture}"),
                        f"{navigate.current_nav_instr_text}",
                        dict(center=geocoding_utils.convert_to_lat_lon(navigate.way_points[navigate.current_way_point_index]), zoom=18, transition = "setView"), #flyTo 
                        True,False, value, no_update,
                        (dbc.Table.from_dataframe(pd.DataFrame(
                            {
                                "in ... metern": navigate.remaining_nav_instr_distances,
                                "Anweisung": navigate.remaining_nav_instr_texts,
                            }), striped=True, bordered=True, hover=True)),
                        #""
                        #position.get_pos()
                        ) 
        
        elif n_clicks == 2:
            return (n_clicks, "Next", 
                        dash.get_relative_path(f"/assets/{route_pictures[1]}"),
                        f"In {navigate.remaining_distance}m: {navigate.current_nav_instr_text}",
                        dict(center=geocoding_utils.convert_to_lat_lon(waypoints[1]), zoom=18, transition = "setView"), #flyTo 
                        True,False, value, no_update,
                        (dbc.Table.from_dataframe(pd.DataFrame(
                            {
                                "in ... metern": l[0:],
                                "Anweisung": route_instructions[0:],
                            }), striped=True, bordered=True, hover=True)),
                       # ""
                        #position.get_pos()
                        ) 
        
        # after last step, restart automatically
        elif n_clicks == len(waypoints):
            #print(f"if nclicks == len: {waypoints[n_clicks-1]}")
            return (0, "Start", 
                    dash.get_relative_path(f"/assets/{route_pictures[-1]}"),
                    f"{route_instructions[-1]}", 
                    dict(center=geocoding_utils.convert_to_lat_lon(waypoints[-1]), zoom=18),
                    False, False, value, no_update,
                    (dbc.Table.from_dataframe(pd.DataFrame(
                            {
                                "in ... metern": l[:1],
                                "Anweisung": route_instructions[-1:],
                            }), striped=True, bordered=True, hover=True)),
                    #""
                    #position.get_pos()
                    )
        
        # if number of clicks is one of the next steps change instruction and picture
        elif n_clicks-1 in step_waypoints:
            #print(f"if nclicks in stepway: {waypoints[n_clicks-1]}")
            index = step_waypoints.index(n_clicks-1)  
            return (n_clicks, "Next", 
                    dash.get_relative_path(f"/assets/{route_pictures[index+1]}"),
                    f"In {route_distances[index]}m: {route_instructions[index+1]}",
                    dict(center=geocoding_utils.convert_to_lat_lon(waypoints[n_clicks-1]), zoom=18),
                    False, False, value, no_update,
                    (dbc.Table.from_dataframe(pd.DataFrame(
                            {
                                "in ... metern": l[index:],
                                "Anweisung": route_instructions[index:],
                            }), striped=True, bordered=True, hover=True)),
                    #""
                    #position.get_pos()
                    )
        
        # normal step further
        #print(f"if nclicks not in stepway: {waypoints[n_clicks-1]}")
        return (n_clicks, "Next", 
                no_update, 
                no_update, 
                dict(center=geocoding_utils.convert_to_lat_lon(waypoints[n_clicks-1]), zoom=18),
                False, False, value, no_update,
                no_update,
                #""
                #position.get_pos()
                )
    # no buttons were clicked
    return (0, "Start", "", "", dict(center=no_update, zoom=no_update), True, True, 0, "")#, "" #, None


# change trafficlight picture
@callback(
    Output("tl_picture","src"),
    Input("tl_picture","src")
)
def tl_pic(src):
    if src == "":
        return dash.get_relative_path(f"/assets/tf_off.png")
    return no_update

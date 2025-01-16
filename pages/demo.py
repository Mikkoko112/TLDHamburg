import dash
from dash import no_update, ctx, callback, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl

import pandas as pd
import time

# import functions and classes
from tldhamburg.frontend.Navigation import Navigation
from tldhamburg.frontend.position import Position
from tldhamburg.frontend import geocoding_utils
from tldhamburg.frontend import get_objects

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

# Main layout
def layout(**kwargs): 
    return dbc.Container(children = [
            dcc.Store(id='data-navigate', data=""), 
            navbar_demo(),
            data_demo(),
            dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Loading..."), close_button=False),
                dbc.ModalBody(html.Div([dbc.Spinner(size="lg")], 
                                       className="centered-spinner",))
            ],
            id="loadingscreen",
            is_open=False,
            backdrop="static",
            centered=True,
        ),
            ],
        fluid = True, # remove the margins
        className="demo-live-container",
        )

# Callback to load data when the app starts
@callback(
    Output('data-navigate', 'data'),
    Input('data-navigate', 'data'),  # Dummy input to trigger on app load
    running=[
        (Output("loadingscreen", "is_open"), True, False)    
    ],
)
def load_data_on_init(dummy_data):
    if dummy_data == "":
        # it will show the map with the markers and the Overview
        global pos, navigate
        pos = Position() # Create a Position object
        navigate = Navigation() # Create a Navigation object
        return "1"
    return no_update

# triggers if you click the route button
# this callback will get the Input for the start and end adresses
# it will give back the coordinates and shows them in the map as a marker
# it also generates a route and show it in the map
@callback(
    Output("startpunkt", "valid"),          # True: shows if the input (departure) is valid (green)
    Output("startpunkt", "invalid"),        # True: shows if the input (departure) is invalid (red)
    Output("endpunkt", "valid"),            # True: shows if the input (destination) is valid (green) 
    Output("endpunkt", "invalid"),          # True: shows if the input (destination) is invalid (red)
    Output("route-button", "n_clicks"),     # set n_clicks to 0 
    Output("start-end-layer", "children"),  # load start and end point into the map
    Output("route-layer", "data"),          # load route (geojson) into the map
    Output("tl-route-layer", "children"),  # load traffic lights into the map
    Output("start-next-button", "disabled", allow_duplicate=True),# True: disables the start/next button if no route is given
    Output("tab-2","disabled"),             # enables the Overview tab
    Output("start-next-button", "n_clicks", allow_duplicate=True), # reset n_clicks if calculating new route

    [State("startpunkt","value"),
     State("endpunkt","value"),
     State("bike-switch", "value"),
     State("radioitems-input", "value"),
     Input("route-button", "n_clicks"),
     ],
     running=[
        (Output("route-button", "disabled"), True, False),
        (Output("route-button", "children"), [dbc.Spinner(size="sm"), " Loading..."], "Route"),
        (Output("map", "center"), [53.549573,9.953330],[53.549573,9.953330]), # during loading for the new route zoom out
        (Output("map", "zoom"),10,10),                                        # to not have a problem with viewing bound 
    ],
    prevent_initial_call=True
)
def check_validity(starttext, endtext, bicycle_mode, route_option, n_clicks): 
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
                    "",
                    True,
                    no_update,
                    0,
                    )
            
            #get route from control
            navigate.update_mode(bicycle_mode,route_option)
            navigate.create_route([start_lon,start_lat], [end_lon, end_lat])
            pos.set_pos(lat=start_lat, lon=start_lon)

            return (is_valid_start, 
                    not is_valid_start, 
                    is_valid_end, 
                    not is_valid_end, 
                    0, 
                    get_objects.get_marker(marker), 
                    navigate.geojson, 
                    get_objects.get_trafficlights(navigate.get_all_trafficlight_coordinates()),  
                    False,
                    False,
                    0,
                    )
    return (False, 
            False, 
            False, 
            False, 
            0, 
            no_update, 
            no_update, 
            no_update, 
            no_update,
            no_update,
            no_update,
            )

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
    Output("start-next-button", "n_clicks", allow_duplicate=True),    # 
    Output("start-next-button", "children"),    # change text from start to next after going one step
    Output("route-picture", "src"),             # change picture for instruction
    Output("route-instruction", "children"),    # change text for instruction
    Output('map', 'viewport'),                  # change view of the map
    Output("prev-button", "disabled"),          # True: disables the prev button
    Output("start-next-button", "disabled", allow_duplicate=True),    # True: disables the start/next button
    Output("restart-button", "disabled"),       # True: disables the restart button
    Output("progress", "value"),                # change progress value 
    Output("prev-button", "n_clicks"),          #
    Output("instruction-overview","children"),  # list all instruction still left
    Output("speed-limit", "children"),          # change the speed limit 
    Output("position", "center"),               # change current position 
    Output("speed-recommendation", "children"), # change speed recommendation

    Input("start-next-button", "n_clicks"),
    Input("prev-button", "n_clicks"),
    Input("restart-button", "n_clicks"),
    Input("route-button", "n_clicks"),
    State("map-store", "data"),

    prevent_initial_call=True
)
def show_instructions(n_clicks, prev, restart, route, store):
    button_id = ctx.triggered_id
    
    # return values
    # no change if no buttons were clicked
    button_text = "Start"
    picture = ""
    text = ""
    # store 
    toggle_prev_button = True
    toggle_startnext_button = False
    toggle_restart_button = True
    progress_value = 0
    prev_nclicks = 0
    remaining_instructions = ""
    speed_limit_text = "Maximal erlaubte Geschwindigkeit: -"
    speed_recommendation_text = ["Fahre ",
                        html.B(" - km/h"), ",",
                        html.Br(),
                        "um ",
                        html.Span("grün", style={"color": "green", "white-space": "pre"}),
                        " zu erreichen."]

    if button_id == "route-button":
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                        {
                            "in ... metern": navigate.remaining_nav_instr_distances,
                            "Anweisung": navigate.remaining_nav_instr_texts,
                        }), striped=True, bordered=True, hover=True))
    # restart the route instructions and picture
    elif button_id == "restart-button":
        n_clicks = 0
        picture = ""
        # update pos with the new waypoint
        lat, lon = navigate.demo_n_clicks(n_clicks+1)
        pos.set_pos(lat, lon)
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                        {
                            "in ... metern": navigate.remaining_nav_instr_distances,
                            "Anweisung": navigate.remaining_nav_instr_texts,
                        }), striped=True, bordered=True, hover=True))
       
    # go one step further or one step back
    elif (button_id == "start-next-button" or button_id == "prev-button") and n_clicks != 0:
        # go one step back
        if button_id == "prev-button":
            n_clicks = n_clicks - 1
        
        elif n_clicks == len(navigate.way_points)+1:
            n_clicks = 0

        # update pos with the new waypoint
        lat, lon = navigate.demo_n_clicks(n_clicks)
        pos.set_pos(lat, lon)

        button_text = "Next" 
        picture = dash.get_relative_path(f"/assets/{navigate.current_nav_instr_picture}")
        text = f"In {navigate.remaining_distance}m: {navigate.current_nav_instr_text}"
        store = dict(center=geocoding_utils.convert_to_lat_lon(navigate.way_points[navigate.current_way_point_index]), zoom=18, transition = "setView")
        toggle_restart_button = False
        toggle_prev_button = False

        # calculate progress to the next trafficlight
        progress_value = navigate.current_progress_next_tl*100
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                        {
                            "in ... metern": navigate.remaining_nav_instr_distances,
                            "Anweisung": navigate.remaining_nav_instr_texts,
                        }), striped=True, bordered=True, hover=True))

        speed_limit_text = f"Maximal erlaubte Geschwindigkeit: {navigate.current_speed_limit}"
        if navigate.status_next_tl == "green":
            speed_recommendation_text = ["Fahre ", html.B("mindestens ", style={"color": "green"}),
                            html.Br(),
                            html.B(f"{navigate.current_recommended_speed} km/h", style={"color": "green"}), 
                            ",",
                            html.Br(),
                            "um ",
                            html.Span("grün", style={"color": "green", "white-space": "pre"}),
                            " zu erreichen."] 
        elif navigate.status_next_tl == "red":
            speed_recommendation_text = ["Fahre ", html.B("maximal ", style={"color": "red"}),
                            html.Br(),
                            html.B(f"{navigate.current_recommended_speed} km/h", style={"color": "red"}), 
                            ",",
                            html.Br(),
                            "um ",
                            html.Span("grün", style={"color": "green", "white-space": "pre"}),
                            " zu erreichen."]  
        # first step: prev button disabled 
        if n_clicks == 1:
            text = f"{navigate.current_nav_instr_text}"
            toggle_prev_button = True

        # after last step, restart automatically
        elif n_clicks == len(navigate.way_points):
            #n_clicks = 0
            toggle_startnext_button = True
            #button_text = "Start"
            picture = dash.get_relative_path(f"/assets/goal.png")
            text = "You arrived at your destination" 
        
    return (n_clicks, button_text, picture, text, store, 
            toggle_prev_button, toggle_startnext_button, toggle_restart_button,
            progress_value, prev_nclicks, remaining_instructions,
            speed_limit_text, pos.get_pos("lonlat"), 
            speed_recommendation_text)

# change trafficlight picture
@callback(
    Output("tl-picture","src"),
    Output("tl-picture-tooltip", "children"),
    Input("start-next-button", "n_clicks"),
    Input("restart-button", "n_clicks"),
    Input("route-button", "n_clicks"),
    prevent_initial_call=True
)
def tl_pic(n_clicks, restart, route):
    button_id = ctx.triggered_id
    if button_id == "restart-button" or button_id == "route-button":
        return dash.get_relative_path(f"/assets/tf_off.png"),"Hier wird der Ampelstatus angezeigt."
    if button_id == "start-next-button" and n_clicks > 0:
        if (navigate.status_next_tl == "") or (navigate.status_next_tl == 9):
            return dash.get_relative_path(f"/assets/tf_off.png"),"Es sind keine Ampeldaten vorhanden."
        elif navigate.status_next_tl == "red":
            return dash.get_relative_path(f"/assets/tf_red.png"),"Hier wird der Ampelstatus angezeigt."
        elif navigate.status_next_tl == "yellow":
            return dash.get_relative_path(f"/assets/tf_yellow.png"),"Hier wird der Ampelstatus angezeigt."
        elif navigate.status_next_tl == "green":
            return dash.get_relative_path(f"/assets/tf_green.png"),"Hier wird der Ampelstatus angezeigt."
    return no_update, no_update

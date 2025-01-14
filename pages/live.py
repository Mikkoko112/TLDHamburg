import dash
from dash import no_update, ctx, callback, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas as pd

# import functions and classes
from tldhamburg.frontend.Navigation import Navigation
from tldhamburg.frontend.position import Position
from tldhamburg.frontend import geocoding_utils
from tldhamburg.frontend import get_objects

# import components of the page
from .components import navbar_live
from .components import data_live

dash.register_page(__name__,
                    path='/live',
                    title='Live: Traffic-Light Navigation',
                    name='Live: Traffic-Light Navigation')

#external CSS stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

# Main layout
def layout(**kwargs): 
    return dbc.Container(children = [
    dcc.Store(id="data-navigate-live", data=""), 
    dcc.Store(id="start-navigation-bool", data=False),
    navbar_live(),
    data_live(),
    dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Loading..."), close_button=False),
                dbc.ModalBody(html.Div([dbc.Spinner(size="lg")], 
                                       className="centered-spinner",)),
            ],
            id="loadingscreen-live",
            is_open=False,
            backdrop="static",
            centered=True,
        ),
    ],
    fluid = True, # remove the margins
    className="demo-live-container",
)

@callback(
    Output('data-navigate-live', 'data'),
    Input('data-navigate-live', 'data'),  # Dummy input to trigger on app load
    running=[
        (Output("loadingscreen-live", "is_open"), True, False)                                    
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
    Output("startpunkt-live", "valid"),          # True: shows if the input (departure) is valid (green)
    Output("startpunkt-live", "invalid"),        # True: shows if the input (departure) is invalid (red)
    Output("endpunkt-live", "valid"),            # True: shows if the input (destination) is valid (green) 
    Output("endpunkt-live", "invalid"),          # True: shows if the input (destination) is invalid (red)
    Output("route-button-live", "n_clicks"),     # set n_clicks to 0 
    Output("start-end-layer-live", "children"),  # load start and end point into the map
    Output("route-layer-live", "data"),          # load route (geojson) into the map
    Output("tl-route-layer-live", "children"),  # load traffic lights into the map
    Output("start-button-live", "disabled"),# True: disables the start button if no route is given
    Output("start-button-live", "n_clicks", allow_duplicate=True),
    Output("tab-2-live","disabled"),             # enables the Overview tab

    [State("startpunkt-live","value"),
     State("endpunkt-live","value"),
     State("bike-switch-live", "value"),
     State("center-store-live", "data"), # center of user-location
     Input("route-button-live", "n_clicks"),
     ],
     running=[
        (Output("route-button-live", "disabled"), True, False),
        (Output("route-button-live", "children"), [dbc.Spinner(size="sm"), " Loading..."], "Route"),
    ],
    prevent_initial_call=True
)
def check_validity(starttext, endtext, bicycle_mode, user_store, n_clicks): 
    marker = [{"id": "departure", "lat": 53.5975929, "lon": 9.9318831},
                  {"id": "destination", "lat": 53.5524079, "lon": 10.0084222}]           
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
                0,
                no_update,
                )
        
        #get route from control
        navigate.update_bicycle_mode(bicycle_mode)
        navigate.create_route([start_lon,start_lat], [end_lon, end_lat])

        return (is_valid_start, 
                not is_valid_start, 
                is_valid_end, 
                not is_valid_end, 
                0, 
                get_objects.get_marker(marker), 
                navigate.geojson, 
                get_objects.get_trafficlights(navigate.get_all_trafficlight_coordinates()),  
                False,
                0,
                False,
                )
    return (no_update, 
            no_update, 
            no_update, 
            no_update, 
            0, 
            no_update, 
            no_update, 
            no_update, 
            no_update,
            no_update,
            no_update,
            )

# stores the center data of the View for the position 
@callback(
    Output('center-store-live', 'data'),
    Input('map-live', 'center'),
    State("map-live", "zoom")
)
def store_map_view(center, zoom):
    if zoom >= 17:
        print(f"neuer Standort: {center}")
        print(f"zoom: {zoom}")
        return center 
    print(f"zoom: {zoom}") 
    return no_update

# go through the steps of the route with the start/next button
# progress shows in the progressbar
@callback(
    Output("route-picture-live", "src"),             # change picture for instruction
    Output("route-instruction-live", "children"),    # change text for instruction           
    Output("progress-live", "value"),                # change progress value 
    Output("instruction-overview-live","children"),  # list all instruction still left
    Output("speed-limit-live", "children"),          # change the speed limit 
    Output("speed-recommendation-live", "children"), # change speed recommendation
    Output("route-layer-live", "data", allow_duplicate=True),          # load route (geojson) into the map
    Output("route-layer-live", "zoomToBounds"), # automatic zoom to bounds of the route
    Output("tl-route-layer-live", "children", allow_duplicate=True),  # load traffic lights into the map
    Output("start-navigation-modal", "is_open"),
    Output("start-navigation-bool", "data"),
    Output("start-freigabe-modal", "is_open"),

    [State("route-layer-live", "data"),
    State("start-navigation-bool", "data"), # if the person is near the route
    Input("center-store-live", "data"), # center of user-location
    Input("start-button-live", "n_clicks"),
    Input("route-button-live", "n_clicks")],
    prevent_initial_call=True
)
def show_instructions(data, start_navigation_bool, user_store, n_clicks, _):
    # return values
    picture = ""
    text = ""
    progress_value = 0
    remaining_instructions = ""
    speed_limit_text = "Maximal erlaubte Geschwindigkeit: -"
    speed_recommendation_text = ["fahre mindestens\t",
                        html.Span("-", style={"color": "green"}),
                        "\tkm/h,", 
                        html.Br(),
                        "um\t",
                        html.Span("grün", style={"color": "green", "white-space": "pre"}),
                        "\tzu erreichen"]
    startNavigation = start_navigation_bool # False at the beginning
    startNavigation_modal = False
    zoomToBounds = False
    button_id = ctx.triggered_id
    modal_freigabe = False
    if button_id == "route-button-live":
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                {
                    "in ... metern": navigate.remaining_nav_instr_distances,
                    "Anweisung": navigate.remaining_nav_instr_texts,
                }), striped=True, bordered=True, hover=True)) 
        zoomToBounds = True 
    elif button_id == "start-button-live":
        if user_store is None:
            modal_freigabe = True
        else:
            # update position
            lon = user_store["lat"]
            lat = user_store["lng"]
            print(f"lat:{lat}, lon:{lon}")
            pos.set_pos(lat, lon)
            startNavigation = navigate.start_navigation(pos)
            startNavigation_modal = not startNavigation 
    if (data and user_store != None):
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                {
                    "in ... metern": navigate.remaining_nav_instr_distances,
                    "Anweisung": navigate.remaining_nav_instr_texts,
                }), striped=True, bordered=True, hover=True)) 
    if startNavigation is True:
        print("start!")
        # update position
        lat = user_store["lat"]
        lon = user_store["lng"]
        pos.set_pos(lat, lon)
        navigate.update_route(pos)
        picture = dash.get_relative_path(f"/assets/{navigate.current_nav_instr_picture}")
        text = f"In {navigate.remaining_distance}m: {navigate.current_nav_instr_text}"

        # calculate progress to the next trafficlight
        progress_value = navigate.current_progress_next_tl*100

        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                        {
                            "in ... metern": navigate.remaining_nav_instr_distances,
                            "Anweisung": navigate.remaining_nav_instr_texts,
                        }), striped=True, bordered=True, hover=True))
        
        speed_limit_text = f"Maximal erlaubte Geschwindigkeit: {navigate.current_speed_limit}"
        if navigate.status_next_tl == "green":
            speed_recommendation_text = ["fahre mindestens\t",
                            html.Span(f"{navigate.current_recommended_speed}", style={"color": "green"}),
                            "\tkm/h,", 
                            html.Br(),
                            "um\t",
                            html.Span("grün", style={"color": "green", "white-space": "pre"}),
                            "\tzu erreichen"] 
        elif navigate.status_next_tl == "red":
            speed_recommendation_text = ["fahre maximal\t",
                            html.Span(f"{navigate.current_recommended_speed}", style={"color": "green"}),
                            "\tkm/h,", 
                            html.Br(),
                            "um\t",
                            html.Span("grün", style={"color": "green", "white-space": "pre"}),
                            "\tzu erreichen"] 
        
    return (picture, text, 
            progress_value, remaining_instructions,
            speed_limit_text, speed_recommendation_text, navigate.geojson, zoomToBounds,
                    get_objects.get_trafficlights(navigate.get_all_trafficlight_coordinates()),
                    startNavigation_modal,startNavigation,modal_freigabe)

# change trafficlight picture
@callback(
    Output("tl-picture-live","src"),
    Output("tl-picture-tooltip-live", "children"),
    Input("center-store-live", "data"), # center of user-location
    Input("route-button-live", "n_clicks"),
    prevent_initial_call=True
)
def tl_pic(data, n_clicks):
    button_id = ctx.triggered_id
    if button_id == "route-button-live":
        return dash.get_relative_path(f"/assets/tf_off.png"),"Hier wird der Ampelstatus angezeigt."
    if (navigate.status_next_tl == "") or (navigate.status_next_tl == 9):
        return dash.get_relative_path(f"/assets/tf_off.png"),"Es sind keine Ampeldaten vorhanden."
    elif navigate.status_next_tl == "red":
        return dash.get_relative_path(f"/assets/tf_red.png"),"Hier wird der Ampelstatus angezeigt."
    elif navigate.status_next_tl == "yellow":
        return dash.get_relative_path(f"/assets/tf_yellow.png"),"Hier wird der Ampelstatus angezeigt."
    elif navigate.status_next_tl == "green":
        return dash.get_relative_path(f"/assets/tf_green.png"),"Hier wird der Ampelstatus angezeigt."
    return no_update, no_update


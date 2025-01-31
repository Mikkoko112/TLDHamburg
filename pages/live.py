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

# register_page signalizes dash that it is a page for the app
dash.register_page(__name__,
                    path="/live",
                    title="Live: Traffic-Light Navigation",
                    name="Live: Traffic-Light Navigation")

# Layout definition
def layout(): 
    return dbc.Container(children = [
    # keep stored data on the client side
    dcc.Store(id="data-navigate-live", data=""), 
    dcc.Store(id="start-navigation-bool", data=False),
    # Modal for initial loading of the page 
    dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Laden..."), close_button=False),
                dbc.ModalBody(html.Div([dbc.Spinner(size="lg")], 
                                       className="centered-spinner",)),
            ],
            id="loadingscreen-live",
            is_open=False,
            backdrop="static",
            centered=True,
        ),
    # update site every 3 seconds
    dcc.Interval(
            id="interval-component",
            interval=3*1000, # in milliseconds
            n_intervals=0
        ),
    # include the navbar
    navbar_live(),
    # include the data component (map and instructions)
    data_live(),
    ],
    fluid = True, # remove the margins
    className="demo-live-container",
)

"""
Callback to load data when the app starts.

Input: dummy input to trigger on app load

Output: it creates global object which are needed in other callbacks
During loading modal will open to make a loading screen. 
"""
@callback(
    Output("data-navigate-live", "data"),
    Input("data-navigate-live", "data"),
    # open modal for loading screen
    running=[
        (Output("loadingscreen-live", "is_open"), True, False)                                    
    ],
)
def load_data_on_init(dummy_data):
    if dummy_data == "":
        global pos, navigate # global: to use the objects in other callbacks
        pos = Position() # Create a Position object
        navigate = Navigation() # Create a Navigation object
        return "1"
    return no_update

"""
Triggers if the route button is clicked and generates the route if start and 
end adresses are found.

Input: start and end adresses; bicycle mode bool; route options value; 
center of user-location; route-button-live click value 

Output: the validation bool of the adresses; 
reset click value of route-button-live; load start and end points in the map as a 
marker; load generated route and traffic lights into the map; disable bool for 
start-button-live; reset n_clicks for start-button-live; 
disable bool for overview tab
"""
@callback(
    Output("startpunkt-live", "valid"),          # True: shows if the input (departure) is valid (green)
    Output("startpunkt-live", "invalid"),        # True: shows if the input (departure) is invalid (red)
    Output("endpunkt-live", "valid"),            # True: shows if the input (destination) is valid (green) 
    Output("endpunkt-live", "invalid"),          # True: shows if the input (destination) is invalid (red)
    Output("route-button-live", "n_clicks"),     # set n_clicks to 0 
    Output("start-end-layer-live", "children"),  # load start and end point into the map
    Output("route-layer-live", "data"),          # load route (geojson) into the map
    Output("tl-route-layer-live", "children"),  # load traffic lights into the map
    Output("start-button-live", "disabled", allow_duplicate=True), # True: disables the start button if no route is given
    Output("start-button-live", "n_clicks", allow_duplicate=True), # set n_clicks to 0
    Output("tab-2-live","disabled"),             # enables the Overview tab

    [State("startpunkt-live","value"),
     State("endpunkt-live","value"),
     State("bike-switch-live", "value"),
     State("radioitems-input-live", "value"),
     State("center-store-live", "data"), # center of user-location
     Input("route-button-live", "n_clicks"),
     ],
     running=[
        (Output("route-button-live", "disabled"), True, False),
        (Output("route-button-live", "children"), [dbc.Spinner(size="sm"), " Loading..."], "Route"),
    ],

    prevent_initial_call=True
)
def check_validity(starttext, endtext, bicycle_mode, route_option, user_store, n_clicks):            
    if starttext or endtext: 
        # initial marker value
        marker = [{"id": "departure", "lat": None, "lon": None},
                {"id": "destination", "lat": None, "lon": None}]
        is_valid_start = True
        is_valid_end = True

        # get the coordinates for the departure and destination
        # if departue should be the user location, use the user location 
        if starttext == "Standort":
            start_lon = user_store["lng"]
            start_lat = user_store["lat"]
        else:
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

        # if start or end adress is not found, show error and do not update 
        # map and route
        if not is_valid_start or not is_valid_end :
            return (is_valid_start, 
                not is_valid_start, 
                is_valid_end, 
                not is_valid_end, 
                0, 
                "", 
                None, 
                "",
                True,
                0,
                True,
                )
        
        # if start and end adress is found
        # get route from control
        navigate.update_mode(bicycle_mode, route_option)
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
    
    # do not update anything, if route button is not clicked
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

"""
Stores the center of the view for the user location.

Input: center and zoom values of the map

Output: save the center in a store variable
"""
@callback(
    Output("center-store-live", "data"),
    Input("map-live", "center"),
    State("map-live", "zoom"),
)
def store_map_view(center, zoom):
    if zoom >= 17:
        return center
    return no_update

"""
Set the user location as departure if button standort-live was clicked.

Input: click value of standort-live button; user location

Output: departure input; modal is_open bool (opens information modal, if gps 
is not activated -> True); reset click value of button standort-live 
"""
@callback(
 Output("startpunkt-live","value"),
 Output("start-freigabe-modal", "is_open", allow_duplicate=True),
 Output("standort-live", "n_clicks"),

 [Input("standort-live", "n_clicks"),   
 State("center-store-live","data")],   

 prevent_initial_call=True
)
def set_location_as_start(n_clicks, user_store):
    input = "Standort" 
    modal_freigabe = False
    if user_store is None:
            modal_freigabe = True
            input = ""
    return input, modal_freigabe, 0

"""
Go through the steps of the route and update the instructions. 
Triggers every 3 seconds or if route or start button was clicked.
If user is not near the route anymore, create new route depending on the new 
location.

Input: route from the geojson; start-navigation-bool (says if the person is near the 
route); center of user location; interval value; click value of the buttons 
start-button-live and route-button-live (depending on which one was triggered)

Output: instruction picture and text; progress for the progressbar; 
instruction-overview (all instruction still left); value for speed limit; 
changes speed-recommendation text; route from the geojson; zoom to bounds bool;
load traffic lights into the map; bool to open or hide start-navigation-modal;
store data information that user is near the route (bool); bool to open or hide
start-freigabe-modal; disable bool for start-button-live
"""
@callback(
    Output("route-picture-live", "src"),             # change picture for instruction
    Output("route-instruction-live", "children"),    # change text for instruction           
    Output("progress-live", "value"),                # change progress value 
    Output("instruction-overview-live","children"),  # list all instruction still left
    Output("speed-limit-live", "children"),          # change the speed limit 
    Output("speed-recommendation-live", "children"), # change speed recommendation
    Output("route-layer-live", "data", allow_duplicate=True), # load route (geojson) into the map
    Output("route-layer-live", "zoomToBounds"),      # True: automatic zoom to bounds of the route
    Output("tl-route-layer-live", "children", allow_duplicate=True), # load traffic lights into the map
    Output("start-navigation-modal", "is_open"),     # modal for information that the user is not near the route
    Output("start-navigation-bool", "data"),         # store bool as information if the user is near the route 
    Output("start-freigabe-modal", "is_open", allow_duplicate=True), # modal for information that the user did not activate gps
    Output("start-button-live", "disabled", allow_duplicate=True), # True: disables the start button if no route is given

    [State("route-layer-live", "data"),
    State("start-navigation-bool", "data"), # if the person is near the route
    State("center-store-live", "data"), # center of user location
    Input("interval-component", "n_intervals"), # updates every 3 seconds
    Input("start-button-live", "n_clicks"),
    Input("route-button-live", "n_clicks")],

    prevent_initial_call=True
)
def show_instructions(data, start_navigation_bool, user_store, intervall, n_clicks, _):
    # initialize return values
    picture = ""
    text = ""
    progress_value = 0
    remaining_instructions = ""
    speed_limit_text = "Maximal erlaubte Geschwindigkeit: -"
    speed_recommendation_text = ["Fahre ",
                        html.B(" - km/h"), ",",
                        html.Br(),
                        "um ",
                        html.Span("grün", style={"color": "green", "white-space": "pre"}),
                        " zu erreichen."]
    startNavigation = start_navigation_bool # False at the beginning
    startNavigation_modal = False
    zoomToBounds = False
    button_id = ctx.triggered_id
    modal_freigabe = False
    start_button_disabled = no_update
    trafficlights = ""

    # change values for variables if route-button was triggered
    if button_id == "route-button-live":
        navigate.start_navigating = False 
        if data != None:
            startNavigation = navigate.start_navigating
            remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                    {
                        "in ... metern": navigate.remaining_nav_instr_distances,
                        "Anweisung": navigate.remaining_nav_instr_texts,
                    }), striped=True, bordered=True, hover=True)) 
            zoomToBounds = True 
        else:
            navigate.geojson = None
    
    elif button_id == "start-button-live":
        # if no center is given, open start-freigabe-modal to inform, that gps
        # needs to be activated
        if user_store is None:
            modal_freigabe = True
        else:
            # update position
            lon = user_store["lat"]
            lat = user_store["lng"]
            pos.set_pos(lat, lon)
            
            # if the user is not near the route, startNavigation will be False
            # and start-navigation-modal will open to inform the user
            startNavigation = navigate.start_navigation(pos)
            startNavigation_modal = not startNavigation 
    
    # update overview tab and traffic light markers
    if (data != None):
        trafficlights = get_objects.get_trafficlights(navigate.get_all_trafficlight_coordinates())
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                {
                    "in ... metern": navigate.remaining_nav_instr_distances,
                    "Anweisung": navigate.remaining_nav_instr_texts,
                }), striped=True, bordered=True, hover=True)) 
    
    # if user is near the route, start navigation and updates variables every 
    # 3 seconds after triggering
    if startNavigation is True:
        # update position
        start_button_disabled = True
        lon = user_store["lat"]
        lat = user_store["lng"]
        pos.set_pos(lat, lon)
        navigate.update_route(pos)

         # update variables for the new center
        picture = dash.get_relative_path(f"/assets/{navigate.current_nav_instr_picture}")
        text = f"In {navigate.remaining_distance}m: {navigate.current_nav_instr_text}"
        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                        {
                            "in ... metern": navigate.remaining_nav_instr_distances,
                            "Anweisung": navigate.remaining_nav_instr_texts,
                        }), striped=True, bordered=True, hover=True))
        
        speed_limit_text = f"Maximal erlaubte Geschwindigkeit: {navigate.current_speed_limit}"
        
        # calculate progress to the next trafficlight
        progress_value = navigate.current_progress_next_tl*100

        # change text for speed recommendation depending on the traffic light status
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
        
    return (picture, text, 
            progress_value, remaining_instructions,
            speed_limit_text, speed_recommendation_text, navigate.geojson, zoomToBounds,
            trafficlights,
            startNavigation_modal,startNavigation,modal_freigabe, start_button_disabled,
            )

"""
Change traffic light picture depending on the light status. 
Triggers if speed-recommendation-live was updated.

Input: center of user location; click value of route-button-live; 
speed-recommendation-live content for triggering the callback

Output: traffic light picture; tooltip for the traffic light picture
"""
@callback(
    Output("tl-picture-live","src"),
    Output("tl-picture-tooltip-live", "children"),

    State("center-store-live", "data"), # center of user location
    Input("route-button-live", "n_clicks"),
    Input("speed-recommendation-live", "children"),

    prevent_initial_call=True
)
def tl_pic(data, n_clicks, intervall):
     # save which button was triggered
    button_id = ctx.triggered_id

    # if new route was calculated, turn traffic light off
    if button_id == "route-button-live":
        return dash.get_relative_path(f"/assets/tf_off.png"),"Hier wird der Ampelstatus angezeigt."
    # change traffic light picture depending on the status of the traffic light
    if (navigate.status_next_tl == "") or (navigate.status_next_tl == 9):
        return dash.get_relative_path(f"/assets/tf_off.png"),"Es sind keine Ampeldaten vorhanden."
    elif navigate.status_next_tl == "red":
        return dash.get_relative_path(f"/assets/tf_red.png"),"Hier wird der Ampelstatus angezeigt."
    elif navigate.status_next_tl == "yellow":
        return dash.get_relative_path(f"/assets/tf_yellow.png"),"Hier wird der Ampelstatus angezeigt."
    elif navigate.status_next_tl == "green":
        return dash.get_relative_path(f"/assets/tf_green.png"),"Hier wird der Ampelstatus angezeigt."
    return no_update, no_update


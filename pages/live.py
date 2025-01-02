import dash
from dash import no_update, callback
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

# it will show the map with the markers and the Overview
pos = Position() # Create a Position object
navigate = Navigation() # Create a Navigation object

# Main layout
def layout(**kwargs): 
    return dbc.Container(children = [
    navbar_live(),
    data_live()
    ],
    fluid = True, # remove the margins
    className="demo-live-container",
)


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
    Output("tab-2-live","disabled"),             # enables the Overview tab
    Output("instruction-overview-live","children",allow_duplicate=True),  # list all instruction 

    [State("startpunkt-live","value"),
     State("endpunkt-live","value"),
     State("bike-switch-live", "switch"),
     Input("route-button-live", "n_clicks"),
     ],
     running=[
        (Output("route-button-live", "disabled"), True, False),
        (Output("route-button-live", "children"), [dbc.Spinner(size="sm"), " Loading..."], "Route"),
        (Output("map-live", "center"), [53.549573,9.953330],[53.549573,9.953330]), # during loading for the new route zoom out
        (Output("map-live", "zoom"),10,10),                                        # to not have a problem with viewing bound 
    ],
    prevent_initial_call=True
)
def check_validity(starttext, endtext, bicycle_mode, n_clicks): 
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
                    no_update,
                    no_update,
                    )
            
            #get route from control
            if bicycle_mode is True:
                navigate.create_route([start_lon,start_lat], [end_lon, end_lat],True)
            else:
                navigate.create_route([start_lon,start_lat], [end_lon, end_lat])
            pos.set_pos(lat=start_lat, lon=start_lon)
            pos.set_pos(lat=start_lat, lon=start_lon)
            navigate.start_navigation(pos)

            return (is_valid_start, 
                    not is_valid_start, 
                    is_valid_end, 
                    not is_valid_end, 
                    0, 
                    get_objects.get_marker(marker), 
                    navigate.geojson, 
                    get_objects.get_trafficlights(navigate.get_all_trafficlight_coordinates()),  
                    False,
                    (dbc.Table.from_dataframe(pd.DataFrame(
                            {
                                "in ... metern": navigate.remaining_nav_instr_distances,
                                "Anweisung": navigate.remaining_nav_instr_texts,
                            }), striped=True, bordered=True, hover=True)), 
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
            )

# stores the data of the View for the whole route 
@callback(
    Output('map-store-live', 'data'),
    Input('map-live', 'center'),
)
def store_map_view(center):
    print(center)
    return center

# go through the steps of the route with the start/next button
# progress shows in the progressbar
@callback(
    Output("route-picture-live", "src"),             # change picture for instruction
    Output("route-instruction-live", "children"),    # change text for instruction
    Output("map-live", "viewport"),                  # change view of the map
    Output("progress-live", "value"),                # change progress value 
    Output("instruction-overview-live","children"),  # list all instruction still left
    Output("speed-limit-live", "children"),          # change the speed limit 

    Input("route-layer-live", "data"),
    Input("map-store-live", "data"), # center of user-location

    prevent_initial_call=True
)
def show_instructions(data, store):
    # return values
    picture = ""
    text = ""
    progress_value = 0
    remaining_instructions = ""
    speed_limit_text = "Maximal erlaubte Geschwindigkeit: -"

    n_clicks = 0 # löschen!
    if data and store!=None:
        # update position
        lat = store["lat"]
        lon = store["lng"]
        pos.set_pos(lat, lon)
        #print(f"{lat},{lon}")
        picture = dash.get_relative_path(f"/assets/{navigate.current_nav_instr_picture}")
        text = f"In {navigate.remaining_distance}m: {navigate.current_nav_instr_text}"
        #store = dict(center=geocoding_utils.convert_to_lat_lon(navigate.way_points[navigate.current_way_point_index]), zoom=18, transition = "setView")

        # calculate progress to the next trafficlight
        progress_value = navigate.current_progress_next_tl*100

        remaining_instructions = (dbc.Table.from_dataframe(pd.DataFrame(
                        {
                            "in ... metern": navigate.remaining_nav_instr_distances,
                            "Anweisung": navigate.remaining_nav_instr_texts,
                        }), striped=True, bordered=True, hover=True))
        
        speed_limit_text = f"Maximal erlaubte Geschwindigkeit: {navigate.current_speed_limit}"

        # first step: # harry fragen
        if n_clicks == 1:
            text = f"{navigate.current_nav_instr_text}"

        # last step: # harry fragen
        elif n_clicks == len(navigate.way_points)-1:
            picture = dash.get_relative_path(f"/assets/goal.png")
            text = "You arrived at your destination" 
        
    return (picture, text, store, 
            progress_value, remaining_instructions,
            speed_limit_text)

# change trafficlight picture
@callback(
    Output("tl-picture-live","src"),
    Input("tl-picture-live","src")
)
def tl_pic(src):
    if src == "":
        return dash.get_relative_path(f"/assets/tf_off.png")
    return no_update


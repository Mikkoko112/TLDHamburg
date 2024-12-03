#from threading import Timer
from flask import Flask, send_from_directory
#from pathlib import Path

import dash
from dash import dcc, html, no_update, ctx, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import dash_bootstrap_components as dbc

from .side_bar import sidebar

from tldhamburg.frontend import APIkeys
from tldhamburg.frontend import * # in __innit__.py __all__ = ["filename.py", "otherfile.py",...]


dash.register_page(__name__,
                    path='/demo',
                    title='Demo: Traffic-Light Navigation',
                    name='Demo: Traffic-Light Navigation')

#external CSS stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

UPLOAD_DIRECTORY = "/Frontend/app_uploaded_files"

ORS_key = APIkeys.ORS_key 
#if not os.path.exists(UPLOAD_DIRECTORY):
#    os.makedirs(UPLOAD_DIRECTORY)

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)

@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

# Initial markers locations and statuses
marker_1 = [{"id": "start", "lat": 53.5533, "lon": 10},
 {"id": "end", "lat": 53.5, "lon": 10}]
 
current_pos = [{"id": "current_pos", "lat": None, "lon": None}]

traffic_lights = [
     {"id": 1, "lat": None, "lon": None, "status": "red"},
     {"id": 2, "lat": None, "lon": None, "status": "green"}
     ]

#marker_url = app.get_asset_url("location_on.png")
# lat: latitude (Breite)
# lon: longitude (Länge

headline = dbc.Row([
        dbc.Col(html.H1("Real-Time Traffic Light Map"), className="text-center")
        ],
        style={"height": "6vh"}
        )

upload = dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and drop or click to select a file to upload."]), 
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),

modal_fileupload = dbc.Col(
    [
        dbc.Button("Laden", id="open-centered", className="mb-3", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Laden: diese Funktion könnt ihr erstmal ignorieren. Man kann erstmal nur Sachen hochladen aber damit nichts anfangen."), close_button=True),
                dbc.ModalBody([
                    html.Div(upload),
                    html.Div("Hochgeladene Dateien:"),
                    html.Div(id="file-list")]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Fertig",
                        id="close-centered",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False,
        ),
    ]
)

# the searchbar with the search field for the start and end location
# and the button to start the search
searchbar = dbc.Row(
            [   
                dbc.Col(
                    [dbc.InputGroup(
                        [dbc.InputGroupText("Id's"),
                        dbc.Input(type="search", id="id_selection", placeholder="8,100,1720,...", value=""),
                        ],
                        className="mb-3",
                        )
                    ], width = "auto"
                ),

                dbc.Col(
                    dbc.Button(
                        "Suchen",id="id_button", color="primary", className="mb-3", n_clicks=0
                        ),
                width="auto"
                ),

                dbc.Col(
                    [dbc.InputGroup(
                        [dbc.InputGroupText("Start"),
                        dbc.Input(type="search", id="startpunkt", placeholder="Informatikum", value=""),
                        dbc.FormFeedback("", type="invalid", id="start_invalid"),
                        dbc.FormFeedback("", type="valid", id="start_valid"),
                        ], 
                        className="mb-3",
                        )
                    ], width = "auto"
                ),
            
                dbc.Col(
                    [dbc.InputGroup(
                        [dbc.InputGroupText("Ziel"),
                        dbc.Input(type="search", id="endpunkt", placeholder="Hauptbahnhof", value=""),
                        dbc.FormFeedback("", type="invalid", id="end_invalid"), 
                        dbc.FormFeedback("", type="valid", id="end_valid"),
                        ],
                        className="mb-3",
                        )  
                    ], width="auto"
                ),
            
                dbc.Col(
                    dbc.Button(
                        "Route",id="route_button", color="primary", className="mb-3", n_clicks=0
                        ),
                width="auto"
                ),
                
                modal_fileupload,
            ],  
            className="g-3 ms-auto flex-nowrap mt-3 mt-md-0", 
            align="center",
            style={"height": "6vh"}
        )

# the navigation bar, there you it will "toggle/collapse" if the window is smaller 
# in this field you can find the searchbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand("Navbar", className="ms-0")),
                    ],
                    align="center",
                    className="g-0",
                ),
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                searchbar,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ], fluid = True,
    ),
    color="secondary",
    dark=True, 
)


next_turn = dbc.Row(
    children=[
        dbc.Col(
            html.Div([
                html.Img(id = "route_picture",
                         src="", 
                         style={"display": "flex",
                                "alignItems": "left", 
                                "width": "20vw",
                               # "height": "35vh",
                                "marginRight": "8px"})
            ],
            ), align = "center",
            
        ),
        dbc.Col(
            html.Div("",
                    id = "route_instruction", 
                    style={"fontSize": "28px", 
                        "display": "flex", 
                        "alignItems": "left", 
                        "marginBottom": "8px", 
                        "marginTop": "8px",
                        }
                        ), 
               align="center",
            )
    ], 
    style={"display": "flex", 
           "alignItems": "left",
            "marginRight": "2vw",
            "height": "40vh"}
)

current_speed = 30

speed = dbc.Row(
        children= [
            dbc.Col(
                dbc.Button("Prev", id = "prev_button", color="secondary", 
                            className="me-1", disabled=True),
                width = "auto",
            ),
            dbc.Col(
                dbc.Button("Start", id = "start_next_button", color="secondary", 
                            className="me-1", disabled=True),
                width = "auto",
            ),
            dbc.Col(
                dbc.Button("Restart", id = "restart_button", color="secondary", 
                            className="me-1", disabled=True),
                width = "auto",
            ),
            dbc.Col(
                    dbc.ListGroup([
                            dbc.ListGroupItem(f"Deine Geschwindigkeit: {current_speed}"),
                            #dbc.ListGroupItem("Item 2"),
                        ],
                        horizontal=True,
                        className="mb-2",
                    ), 
            ),
        ],
        style={"display": "flex", 
           "alignItems": "left",
            "marginLeft": "2vw"}
)

necessary_speed = 29

speed_recommendation = html.Div([
                        html.Span("fahre mindestens\t"),
                        html.Span(f"{necessary_speed}", style={"color": "green"}),
                        html.Span("\tkm/h, um\t"),
                        html.Span("grün", style={"color": "green", "white-space": "pre"}),
                        html.Span("\tzu erreichen")],
                        style={"fontSize": "28px", 
                            "display": "flex", 
                            "alignItems": "left", 
                            "marginBottom": "8px", 
                            "marginTop": "8px",
                            "marginLeft": "2vw",
                            "marginRight": "2vw",  
                            "gap": "5px",
                            } 
                            )
    

# progress bar
progress = html.Div(
                    [dbc.Progress(id = "progress", value=0, 
                                striped=True, 
                                animated=False, 
                                className="mb-3",
                                color="info",
                                style={"height": "25px",
                                       "marginLeft": "2vw",
                                       "marginRight": "2vw"}
                        )
                    ], 
                    )             
                

# it will show the map with the markers and the Overview
geojson = 1
position = position.Position() # Create a position Object
data = dbc.Row([
                dbc.Col([
                    dcc.Store(id='map-store', data={"center": None, "zoom": None}),  # Store to keep the map zoom level
                    dl.Map(id = "map", center=position.get_pos(), zoom=14,
                    children=[
                        dl.TileLayer(),
                        dl.GeoJSON(id="route-layer", data=None, options={"color": "blue"}, zoomToBounds=True),
                        #dl.Circle(id="position", center=position.get_pos(), radius=20),
                        dl.LayerGroup(id="tl-id-layer"),  # This is where markers will be added
                        dl.LayerGroup(id="start-end-layer"),
                        dl.LayerGroup(id="tf-route-layer"),
                        dl.LocateControl(locateOptions={'enableHighAccuracy': True, 
                                "setView": False, 
                                "watch": True, 
                                "maxZoom": 17,
                                },
                                showCompass = False),
                        dl.ScaleControl(position="bottomleft", imperial=False), #shows the scala 
                        dl.FullScreenControl()
                        ], 
                    style={'width': '100%', 'height': '84vh'})
                    ]),
                
                dbc.Col(children= [#html.Div("Übersicht: "), html.Div(id="coordinates_start", children = ""), 
                           #html.Div(id="coordinates_end", children=""),
                           next_turn,
                           speed,
                           speed_recommendation,
                           progress],
                    style={'width': '100%', 'height': '84vh'}
                    ),
            ],
            className="g-1", #change Row gutter (distance between the Columns)
        )

# Main layout
layout = dbc.Container(children = [
    sidebar(),
    headline,
    navbar,
    data
    ],
    fluid = True, # remove the margins
    style={'padding': 0,
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
            # Rasmus Daten mit Ampeln!
            #route = get_route.Route()
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

    #stores the data of the View for the whole route
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


# add callback for toggling the collapse on small screens
@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# opens the window for the upload 
@callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# upload data and show which files you added
@callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            upload_file.save_file(name, data)

    files = upload_file.uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        option = [{"label": f"{filename}", "value": i} for i,filename in enumerate(files)]
        filelist = dbc.RadioItems(options= option, value=False, id="radioitems-input",)
        return filelist
    

# this will show the Ids of the traffic lights and their current status in the map
@callback(
    Output("tl-id-layer","children"),
    [Input("id_button","n_clicks"),
    State("id_selection","value")], 
    prevent_initial_call=True  
)
def find_id_and_show_in_map(n_clicks, ids):
    #things = Things.Things([8,100,1720])
    ids_list = [8,100,1720]
    if n_clicks:
        if(ids != ""):
            ids_list = list(map(int, ids.split(",")))
            #things = Things.Things(ids_list)
            #observations = things.get_tl_observations(ids_list, n_obsrvtns=1, phnTime=True)
            #coordinations = things.get_coordinates()
            
            #return get_objects.get_marker_id(coordinations, observations)
        #return get_objects.get_marker_id(things.get_coordinates(),things.get_tl_observations([8,100,1720], n_obsrvtns=1, phnTime=True))
    return get_objects.get_marker_id(ids_list)

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
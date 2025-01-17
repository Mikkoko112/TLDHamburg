import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_leaflet as dl

# dropdown named Menu, there the pages can be selected
# shows the pages the app has
# by clicking on the page names, change to the corresponding page
# on the right of the navbar
def dropdown():
    return dbc.DropdownMenu(
        label="Menü",
        color="secondary",
        align_end=True,
        children=[
             dbc.NavLink(
                    dbc.DropdownMenuItem(page["name"], className="ms-2"),
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
        ] 
    )                  

# the searchbar with the search field for the start and end location
# and the button to start the search
# locates in the navbar
def searchbar_demo(): 
    return  dbc.Row(
          [
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Start"),
                        dbc.Input(type="search", id="startpunkt", placeholder="Informatikum", value=""),
                        dbc.FormFeedback("", type="invalid", id="start-invalid"),
                        dbc.FormFeedback("", type="valid", id="start-valid"),
                    ], 
                    ), 
                    width="auto",
                ),
            dbc.Col(   
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Ziel"),
                        dbc.Input(type="search", id="endpunkt", placeholder="Hauptbahnhof", value=""),
                        dbc.FormFeedback("", type="invalid", id="end-invalid"), 
                        dbc.FormFeedback("", type="valid", id="end-valid"),
                    ],
                    ), 
                    width="auto",
                ),
            dbc.Col(
            children=[
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "Route",
                            id="route-button",
                            color="primary",
                            n_clicks=0,
                        ),
                        dbc.DropdownMenu(
                            label="",
                            color="primary",
                            align_end=True,
                            group=True,
                            children=[
                                dbc.DropdownMenuItem("Optionen zur Routenberechnung", header=True),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Ampelschaltung betrachten", "value": "phases"},
                                        {"label": "Möglichst wenige Ampeln", "value": "count"},
                                    ],
                                    value="phases",
                                    id="radioitems-input",
                                    inline=False,
                                    style = {"display": "block", "margin-left": "15px", "margin-right": "15px"},  #Aligns radio items vertically
                                )
                            ]
                        ),
                    ]
                ),
            ]
        ),
            ],
            className="flex-searchbar-container"
        )

def searchbar_live(): 
    return  dbc.Row(
          [
            dbc.Col(
                dbc.ButtonGroup([
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Start"),
                        dbc.Input(type="search", id="startpunkt-live", placeholder="Informatikum", value=""),
                        dbc.FormFeedback("", type="invalid", id="start-invalid-live"),
                        dbc.FormFeedback("", type="valid", id="start-valid-live"),
                    ], 
                    ), 
                dbc.Button(
                    children=html.A(children=[
                            html.Img(id = "standort-picture", src=dash.get_relative_path(f"/assets/my_location.png"), height=30)]),
                    id="standort-live",
                    color="light",
                    n_clicks=0,
                ),
                dbc.Tooltip(
                    "aktuellen Standort als Startort wählen",
                    target="standort-picture",
                ),
            ]),
            width="auto",
            ),
            dbc.Col(   
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Ziel"),
                        dbc.Input(type="search", id="endpunkt-live", placeholder="Hauptbahnhof", value=""),
                        dbc.FormFeedback("", type="invalid", id="end-invalid-live"), 
                        dbc.FormFeedback("", type="valid", id="end-valid-live"),
                    ],
                    ), 
                    width="auto",
                ),
            dbc.Col(
            children=[
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "Route",
                            id="route-button-live",
                            color="primary",
                            n_clicks=0,
                        ),
                        dbc.DropdownMenu(
                            label="",
                            color="primary",
                            align_end=True,
                            group=True,
                            children=[
                                dbc.DropdownMenuItem("Optionen zur Routenberechnung", header=True),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Ampelschaltung betrachten", "value": "phases"},
                                        {"label": "Möglichst wenige Ampeln", "value": "count"},
                                    ],
                                    value="phases",
                                    id="radioitems-input-live",
                                    inline=False,
                                    style = {"display": "block", "margin-left": "15px", "margin-right": "15px"},  #Aligns radio items vertically
                                )
                            ]
                        ),
                    ]
                ),
            ]
        ),
            ],
            className="flex-searchbar-container"
        )

# the navigation bar
# in this field you can find the searchbar and the dropdown menu
def navbar_demo():
    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                # Use row and col to control vertical alignment of logo / brand
                    dbc.Row( 
                        [
                        dbc.NavbarBrand("Demo: Traffic-Light Navigation", 
                                        style={"color": "white"},
                            ),
                        ],
                    ),
                ),
                searchbar_demo(),
                dbc.Switch(
                    id="bike-switch",
                    label=html.A(children=[
                            html.Img(id = "bike-picture", src=dash.get_relative_path(f"/assets/bike.png"), height=30)]),
                    value=False, className="flex-bikemode-container",
                ),
                dbc.Tooltip(
                    "Fahrradmodus: beim Fahrradmodus wird die maximale Geschwindigkeit"
                    " auf 20 km/h beschränkt",
                    target="bike-picture",
                ),
                dropdown(),
            ], 
            fluid = True, 
        ),
        className="navbar-container",
        color="secondary",
    )

def navbar_live():
    return dbc.Navbar(
        dbc.Container(
            [
                html.A(
                # Use row and col to control vertical alignment of logo / brand
                    dbc.Row( 
                        [
                        dbc.NavbarBrand("Live: Traffic-Light Navigation", 
                                        style={"color": "white"},
                            ),
                        ],
                    ),
                ),
                searchbar_live(),
                dbc.Switch(
                    id="bike-switch-live",
                    label=html.A(children=[
                            html.Img(id = "bike-picture", src=dash.get_relative_path(f"/assets/bike.png"), height=30)]),
                    value=False, className="flex-bikemode-container",
                ),
                dbc.Tooltip(
                    "Fahrradmodus: beim Fahrradmodus wird die maximale Geschwindigkeit"
                    " auf 20 km/h beschränkt",
                    target="bike-picture",
                ),
                dropdown(),
            ], 
            fluid = True, 
        ),
        className="navbar-container",
        color="secondary",
    )

# shows instruction: a picture and a text
def next_turn_demo(): 
    return dbc.Row(
    children=[
        dbc.Col(
            html.Div([
                html.Img(id = "route-picture",
                         src="", 
                         className="picture-container")
            ],), 
        ),
        dbc.Col(
            html.Div("",
                    id = "route-instruction", 
                    className="instruction-container"
            ), 
        )
    ], 
    className="flex-container-top",
)

def next_turn_live(): 
    return dbc.Row(
    children=[
        dbc.Col(
            html.Div([
                html.Img(id = "route-picture-live",
                         src="", 
                         className="picture-container")
            ],), 
        ),
        dbc.Col(
            html.Div("",
                    id = "route-instruction-live", 
                    className="instruction-container"
            ), 
        )
    ], 
    className="flex-container-top",
)

# buttons for clicking through the route in the demo page
# also shows the maximal speed allowed
def control_demo():
    return dbc.Row(
        children= [
            dbc.Col(
                dbc.Button("Zurück", id = "prev-button", color="secondary", 
                            disabled=True),
                width = "auto",
            ),
            dbc.Col(
                dbc.Button("Weiter", id = "start-next-button", color="secondary", 
                            disabled=True, n_clicks=0),
                width = "auto",
            ),
            dbc.Col(
                dbc.Button("Neustart", id = "restart-button", color="secondary", 
                            disabled=True),
                width = "auto",
            ),
            dbc.Col(
                    dbc.ListGroup([
                        dbc.ListGroupItem("Maximal erlaubte Geschwindigkeit: -", 
                                          id="speed-limit"),
                        ],
                    ), 
                    width = "auto",
            ),
        ],
        className="flex-container-control",
)

# shows the maximal speed allowed - live
def control_live():
    return dbc.Row(
        children= [
            dbc.Col(
                dbc.Button("Start", id = "start-button-live", color="secondary", 
                            disabled=True),
                width = "auto",
            ),
            #dbc.Col(
            #    dbc.Button("Gesamtroute", id = "overview-button-live", color="secondary", 
            #                disabled=True),
            #    width = "auto",
            #),
            dbc.Col(
                    dbc.ListGroup([
                            dbc.ListGroupItem("Maximal erlaubte Geschwindigkeit: -", 
                                              id="speed-limit-live"),
                        ],
                    ), 
                    width = "auto",
            ),
        ],
       className="flex-container-control"
)

# says how fast you should drive
# and 
# picture of a traffic light 
# standard: off
# can be changed to green, yellow and red
def speed_recommendation_demo(): 
    return dbc.Row(children=
            [dbc.Col(
                html.Div(html.P(["Fahre ", 
                        html.B("- km/h"), ",",
                        html.Br(),
                        "um ",
                        html.Span("grün", style={"color": "green", "white-space": "pre"}),
                        " zu erreichen."], id="speed-recommendation"),
                    ),className="speed-recommendation-container",
                ),
            dbc.Col(
                html.Div([
                    html.Img(id = "tl-picture", src=dash.get_relative_path(f"/assets/tf_off.png"))
                ],
                className="tl-container",
                ),
            ),
            dbc.Tooltip(
                    "Hier wird der Ampelstatus angezeigt.",
                    target="tl-picture",
                    id="tl-picture-tooltip",
                    placement="right",
                ),
            ],
        className="flex-container-bottom",
    )

def speed_recommendation_live(): 
    return dbc.Row(children=
            [dbc.Col(
                html.Div(html.P(["Fahre ",
                        html.B("- km/h"), ",",
                        html.Br(),
                        "um ",
                        html.Span("grün", style={"color": "green", "white-space": "pre"}),
                        " zu erreichen."], id="speed-recommendation-live"),
                    ), className="speed-recommendation-container",
                ),
            dbc.Col(
                html.Div([
                    html.Img(id = "tl-picture-live", src=dash.get_relative_path(f"/assets/tf_off.png"))
                ],
                className="tl-container",
                ),
            ),
            dbc.Tooltip(
                    "Hier wird der Ampelstatus angezeigt.",
                    target="tl-picture-live",
                    id="tl-picture-tooltip-live",
                    placement="right",
                ),
            ],
        className="flex-container-bottom",
    )
          
# progress bar for the next traffic light
def progress_demo():
    return html.Div(
                    [dbc.Progress(id = "progress", value=0, 
                                striped=True, 
                                animated=False, 
                                color="info",
                                className="progress-container",
                    )], 
                    ) 

def progress_live():
    return html.Div(
                    [dbc.Progress(id = "progress-live", value=0, 
                                striped=True, 
                                animated=False, 
                                color="info",
                                className="progress-container",
                    )], 
                    ) 

# overview of all steps remaining
def overview_demo():
    return dbc.Col(children=
            [
                html.Div("", id="instruction-overview")
            ],
            className="overview-container",
            )

def overview_live():
    return dbc.Col(children=
            [
                html.Div("", id="instruction-overview-live")
            ],
            className="overview-container",
            )

# the map on the left side and on the right side the route instructions
def data_demo():
    return dbc.Row([
                dbc.Col([
                    dcc.Store(id='map-store', data={"center": None, "zoom": None}),  # Store to keep the map zoom level
                    dl.Map(id = "map", center=[53.549573,9.953330], zoom=10,
                    children=[
                        dl.TileLayer(),
                        dl.GeoJSON(id="route-layer", data=None, options={"color": "blue"}, zoomToBounds=True),
                        dl.Circle(id="position", center=(0,0), radius=10),
                        dl.LayerGroup(id="start-end-layer"),
                        dl.LayerGroup(id="tl-route-layer"),
                        dl.ScaleControl(position="bottomleft", imperial=False), #shows the scala 
                        dl.FullScreenControl()
                        ], 
                    className="left-container",
                    ),],),

                   dbc.Col(dbc.Tabs(
                        [
                            dbc.Tab(
                            dbc.Col(children= 
                                [
                                next_turn_demo(),
                                control_demo(),
                                speed_recommendation_demo(),
                                progress_demo()
                                ],
                            ), 
                            label="Instruktion",tab_id="tab-1-demo",
                            ),
                            dbc.Tab(overview_demo(), 
                                    label="Übersicht", 
                                    disabled=True,
                                    id="tab-2")
                        ], active_tab="tab-1-demo",
                    ))       
            ],
        className="left-container", 
        )

def data_live():
    return dbc.Row([
                dbc.Col([
                    dcc.Store(id='map-store-live', data={"center": [53.549573,9.953330], "zoom": 10}),  # Store to keep the map zoom level
                    dcc.Store(id='center-store-live', data=None),  # Store to keep the map zoom level
                    dl.Map(id = "map-live", center=[53.549573,9.953330], zoom=10, 
                           #zoomControl = False, scrollWheelZoom = False, doubleClickZoom = False,
                           #touchZoom = False, dragging = False,
                    children=[
                        dl.TileLayer(),
                        dl.GeoJSON(id="route-layer-live", data=None, options={"color": "blue"}, zoomToBounds=True),
                        dl.LayerGroup(id="start-end-layer-live"),
                        dl.LayerGroup(id="tl-route-layer-live"),
                        dl.LocateControl(position="topleft",id="locate-control-live", 
                                         cacheLocation = True, returnToPrevBounds = True,
                                locateOptions={'enableHighAccuracy': True, 
                                "setView": True, 
                                "watch": True, 
                                "minZoom": 17,
                                },
                                ),
                        dl.ScaleControl(position="bottomleft", imperial=False), #shows the scala 
                        dl.FullScreenControl()
                        ], 
                    className="left-container", 
                    ),]),

                    dbc.Col(dbc.Tabs(
                        [
                            dbc.Tab(
                            dbc.Col(children= 
                                [
                                next_turn_live(),
                                control_live(),
                                speed_recommendation_live(),
                                progress_live(),
                                ],
                            ), 
                            label="Instruktion", tab_id="tab-1-live", 
                            ),
                            dbc.Tab(overview_live(), 
                                    label="Übersicht", 
                                    disabled=True,
                                    id="tab-2-live")
                        ], active_tab="tab-1-live",
                    )),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Information")),
                        dbc.ModalBody("Um die Navigation zu starten, nähern Sie sich bitte der Route."),
                    ],
                    id="start-navigation-modal",
                    is_open=False,
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Information")),
                        dbc.ModalBody("Um die Navigation zu starten, müssen Sie die Standortfreigabe aktivieren."),
                    ],
                    id="start-freigabe-modal",
                    is_open=False,
                ),
                # Hidden button for programmatic clicking
                #html.Button('Get GPS', id='get-gps-button', n_clicks=0), #style={'display': 'none'}),
                # Store components to store latitude and longitude
                #html.Div(children="hello",id='store-latitude',),#style={'display': 'none'}),
                #html.Div(id='store-longitude',),#style={'display': 'none'}), 
                #html.Div(id="get-gps"),
            ],
            className="left-container", 
        )


# components only for start site ----------------------------------------------

# headline for the start site
def headline():
    return html.H1("Thema: Analyse von Ampelschaltungsdaten in Hamburg",
                    className="text-center")

# text for the start site
def info():
    return html.Div(
            html.P([
        "Ziel des Projektes ist es, die Daten des Transparenzportal Hamburgs zur Optimierung von Navigationen zu verwenden. ", 
        "Dabei wird die Navigation von Autos betrachtet. ",
        "Indem eine Vorhersage der Ampelschaltung ermittelt wird, wird eine Route berechnet, die eine optimale Strecke unter Berücksichtigung der Ampelschaltung ist. ",
        "Als Ausgang werden die letzten aktuellen Daten der Ampeln verwendet und diese für die Berechnung der Vorhersage verwendet. ",
        "Durch eine graphische App-Oberfläche ist eine geeignete Visualisierung vorhanden für den Benutzer.",
        html.Br(),
        html.Br(),
        "Außerdem wird der aktuelle Standort des Nutzers live angezeigt und bei Abwegen der Route, registriert das Programm dies und berechnet anhand der aktuellen Standortdaten eine neue Route. ",
        "Zusätzliche Informationen, wie von anderen Navigationsanbieter bekannt, wie Geschwindigkeit und Gesamtentfernung werden dem Nutzer angezeigt für die jeweilige Route."] #ungefähre Gesamtzeit der Strecke
    ), className="bg-primary bg-opacity-10 text-dark rounded small p-2 info-container-left ")

def contributors():
    return html.Div(
            html.P([
                "Projekt von der Universität Hamburg",
                html.Br(),
                html.Br(),
                "Mitwirkende:",
                html.Br(),
                "Caspar Kiehn,",
                html.Br(),
                "Mikko Kormann,",
                html.Br(),
                "Stevan Miladinovic,",
                html.Br(),
                "Berenike Rutz,",
                html.Br(),
                "Helge Rasmus Steen,",
                html.Br(),
                "Teodor Terziev und",
                html.Br(),
                "Harry Zick",
                html.Br(),
                html.Br(),"Großer Dank geht raus an: ",
                html.Br(),
                "Prof. Dr. Matthias Rarey",
                html.Br(),
                "Ole Berg",
                html.Br(),
                "Tobias Harren"]
    ), 
    className="float-end bg-primary bg-opacity-10 text-dark rounded small p-2 info-container-right")
 
# Define the card_left component
def card_left(): 
    return dbc.Card(
    [
        html.Div(id="link-left-card",
            children=[
                dbc.CardImg(
                    id="img-left-card", 
                    src=dash.get_relative_path(f"/assets/HH_Flagge_links.png"),
                    top=True,
                ),
                dbc.CardImgOverlay(
                    dbc.CardBody(
                        [
                            html.H4("Demo", className="card-title"),
                            html.P(
                                "Navigation wird nicht mit Live-Daten verfolgt. "
                                "Die einzelnen Schritte der Navigation kann einzeln durchgegangen werden. "
                                "Nicht geeignet für eine richtige Navigation. "
                                "Dient zur Veranschaulichung des Systems.",
                                className="card-text",
                            ),
                        ],
                    ),
                ),
            ]
        )
    ],
    className="card-container",
    id="left-card",
)    

# Define the card_right component
def card_right():
    return dbc.Card(
    [
        html.Div( id="link-right-card",
            children=[ 
                dbc.CardImg(id="img-right-card",
                    src=dash.get_relative_path(f"/assets/HH_Flagge_rechts.png"),
                    top=True,
                ),
                dbc.CardImgOverlay(
                    dbc.CardBody(
                        [
                            html.H4("Live", className="card-title"),
                            html.P(
                                "Navigation wird mit Live-Daten verfolgt. "
                                "Benötigt Zugriffsrecht auf Standortfreigabe. "
                                "Kann zur Navigation verwendet werden.",
                                className="card-text",
                            ),
                        ],
                    ),
                ), 
            ]
        )    
    ],
    className="card-container",
    id="right-card",
)  

# information texts and cards for the starting page
def components_startseite():
    return dbc.Row(children=[
        dbc.Col(info()), #Include information text 
        dbc.Col(children=[html.Div(children=[card_left(),card_right()], 
                                   className="card-components-container")]), # Include the cards
        dbc.Col(contributors()),
    ], 
    className="startseite-components-container",
    )
   
    


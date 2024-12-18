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
        ],
    )                  

# the searchbar with the search field for the start and end location
# and the button to start the search
# locates in the navbar
def searchbar(): 
    return  dbc.Row(
          [
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Start"),
                        dbc.Input(type="search", id="startpunkt", placeholder="Informatikum", value=""),
                        dbc.FormFeedback("", type="invalid", id="start_invalid"),
                        dbc.FormFeedback("", type="valid", id="start_valid"),
                    ], 
                    ), 
                    width="auto",
                ),
            dbc.Col(   
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Ziel"),
                        dbc.Input(type="search", id="endpunkt", placeholder="Hauptbahnhof", value=""),
                        dbc.FormFeedback("", type="invalid", id="end_invalid"), 
                        dbc.FormFeedback("", type="valid", id="end_valid"),
                    ],
                    ), 
                    width="auto",
                ),
            dbc.Col(
                 dbc.Button(
                    "Route",id="route_button", color="primary", n_clicks=0,
                    ), 
                    width = "auto",
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
                        dbc.NavbarBrand("Real-Time Traffic Light Map: Demo", 
                                        style={"color": "white"},
                            ),
                        ],
                    ),
                ),
                searchbar(),
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
                        dbc.NavbarBrand("Real-Time Traffic Light Map: Live", 
                                        style={"color": "white"},
                            ),
                        ],
                    ),
                ),
                searchbar(),
                dropdown(),
            ], 
            fluid = True, 
        ),
        className="navbar-container",
        color="secondary",
    )

# shows instruction: a picture and a text
def next_turn(): 
    return dbc.Row(
    children=[
        dbc.Col(
            html.Div([
                html.Img(id = "route_picture",
                         src="", 
                         className="picture-container")
            ],), 
        ),
        dbc.Col(
            html.Div("",
                    id = "route_instruction", 
                    className="instruction-container"
            ), 
        )
    ], 
    className="flex-container-top",
)

# buttons for clicking through the route in the demo page
# also shows the maximal speed allowed
def control_demo(current_speed):
    return dbc.Row(
        children= [
            dbc.Col(
                dbc.Button("Prev", id = "prev_button", color="secondary", 
                            disabled=True),
                width = "auto",
            ),
            dbc.Col(
                dbc.Button("Start", id = "start_next_button", color="secondary", 
                            disabled=True),
                width = "auto",
            ),
            dbc.Col(
                dbc.Button("Restart", id = "restart_button", color="secondary", 
                            disabled=True),
                width = "auto",
            ),
            dbc.Col(
                    dbc.ListGroup([
                        dbc.ListGroupItem(f"Maximal erlaubte Geschwindigkeit: {current_speed}", id="current-speed"),
                        ],
                    ), 
                    width = "auto",
            ),
        ],
        className="flex-container-control",
)

# shows the maximal speed allowed
def control_live(current_speed):
    return dbc.Row(
        children= [
            dbc.Col(
                    dbc.ListGroup([
                            dbc.ListGroupItem(f"Maximal erlaubte Geschwindigkeit: {current_speed}", id="current-speed"),
                        ],
                    ), 
                    width = "auto",
            ),
        ],
       className=".flex-container-control"
)

# says how fast you should drive
# and 
# picture of a traffic light 
# standard: off
# can be changed to green, yellow and red
def speed_recommendation(necessary_speed): 
    return dbc.Row(children=
            [dbc.Col(
                html.Div(html.P(["fahre mindestens\t",
                        html.Span(f"{necessary_speed}", style={"color": "green"}),
                        "\tkm/h,", 
                        html.Br(),
                        "um\t",
                        html.Span("grün", style={"color": "green", "white-space": "pre"}),
                        "\tzu erreichen"],),
                    ),
                ),
            dbc.Col(
                html.Div([
                    html.Img(id = "tl_picture", src="")
                ],
                className="tl-container",
                ),
            )],
        className="flex-container-bottom",
    )
              
# progress bar for the next traffic light
def progress():
    return html.Div(
                    [dbc.Progress(id = "progress", value=0, 
                                striped=True, 
                                animated=False, 
                                color="info",
                                className="progress-container",
                    )], 
                    ) 

# overview of all steps remaining
def overview():
    return dbc.Col(children=
            [
                html.Div("", id="instruction-overview")
            ],
            className="overview-container",
            )

# the map on the left side and on the right side the route instructions
def data_demo(position):
    return dbc.Row([
                dbc.Col([
                    dcc.Store(id='map-store', data={"center": None, "zoom": None}),  # Store to keep the map zoom level
                    dl.Map(id = "map", center=position.get_pos(), zoom=14,
                    children=[
                        dl.TileLayer(),
                        dl.GeoJSON(id="route-layer", data=None, options={"color": "blue"}, zoomToBounds=True),
                        #dl.Circle(id="position", center=position.get_pos(), radius=20),
                        dl.LayerGroup(id="start-end-layer"),
                        dl.LayerGroup(id="tl-route-layer"),
                        dl.LocateControl(locateOptions={'enableHighAccuracy': True, 
                                "setView": False, 
                                "watch": True, 
                                "maxZoom": 17,
                                },
                                showCompass = False),
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
                                next_turn(),
                                control_demo("-"),
                                speed_recommendation("-"),
                                progress()
                                ],
                            ), 
                            label="Instruktion",tab_id="tab-1-demo",
                            ),
                            dbc.Tab(overview(), 
                                    label="Übersicht", 
                                    disabled=True,
                                    id="tab-2")
                        ], active_tab="tab-1-demo",
                    ))       
            ],
        className="left-container", 
        )

def data_live(position):
    return dbc.Row([
                dbc.Col([
                    dcc.Store(id='map-store', data={"center": None, "zoom": None}),  # Store to keep the map zoom level
                    dl.Map(id = "map", center=position.get_pos(), zoom=14,
                    children=[
                        dl.TileLayer(),
                        dl.GeoJSON(id="route-layer", data=None, options={"color": "blue"}, zoomToBounds=True),
                        #dl.Circle(id="position", center=position.get_pos(), radius=20),
                        #dl.LayerGroup(id="tl-id-layer"),  # This is where markers will be added
                        dl.LayerGroup(id="start-end-layer"),
                        dl.LayerGroup(id="tl-route-layer"),
                        dl.LocateControl(locateOptions={'enableHighAccuracy': True, 
                                "setView": False, 
                                "watch": True, 
                                "maxZoom": 17,
                                },
                                showCompass = False),
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
                                next_turn(),
                                control_live("-"),
                                speed_recommendation("-"),
                                progress()
                                ],
                            ), 
                            label="Instruktion", tab_id="tab-1-live", 
                            ),
                            dbc.Tab(overview(), 
                                    label="Übersicht", 
                                    disabled=True,
                                    id="tab-2")
                        ], active_tab="tab-1-live",
                    ))              
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
        "Indem eine Vorhersage der Ampelschaltung ermittelt wird, wird eine Route berechnet, die eine optimale Strecke unter Berücksichtigung der Ampel-schaltung ist. ",
        "Als Ausgang werden die letzten aktuellen Daten der Ampeln verwendet und diese für die Berechnung der Vorhersage verwendet. ",
        "Durch eine graphische App-Oberfläche ist eine geeignete Visualisierung vorhanden für den Benutzer.",
        html.Br(),
        html.Br(),
        "Außerdem wird der aktuelle Standort des Nutzers live angezeigt und bei Abwegen der Route, registriert das Programm dies und berechnet anhand der aktuellen Standortdaten eine neue Route. ",
        "Zusätzliche Informationen, wie von anderen Navigations-anbieter bekannt, wie Geschwindigkeit, ungefähre Gesamtzeit der Strecke und Gesamtentfernung werden dem Nutzer angezeigt für die jeweilige Route."]
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
                "Rasmus Steen,",
                html.Br(),
                "Teodor Terziev und",
                html.Br(),
                "Harry Zick",
                html.Br(),
                html.Br(),"Großer Dank geht raus an "]
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
                                "Dient zur Anschaulichung des Systems.",
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
        dbc.Col(card_left()), # Include the cards
        dbc.Col(card_right()),
        dbc.Col(contributors()),
    ], 
    className="startseite-components-container",
    )
   
    


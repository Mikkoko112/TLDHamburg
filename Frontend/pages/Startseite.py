import dash
from dash import Dash, html, dcc 
import dash_bootstrap_components as dbc
from .components import sidebar

dash.register_page(__name__,
                    path='/',
                    title='Startseite',
                    name='Startseite')


'''layout = html.Div([
    html.H1('Multi-page app with Dash Pages'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ])
])
'''
text = ["Thema: Analyse von Ampelschaltungsdaten in Hamburg",
        html.Br(), html.Br(),
        "Ziel des Projektes ist es, die Daten des Transparenzportal Hamburgs zur Optimierung von Navigationen zu verwenden. ", 
        "Dabei wird die Navigation von Autos betrachtet. ",
        "Indem eine Vorhersage der Ampelschaltung ermittelt wird, wird eine Route berechnet, die eine optimale Strecke unter Berücksichtigung der Ampelschaltung ist. ",
        "Als Ausgang werden die letzten aktuellen Daten der Ampeln verwendet und diese für die Berechnung der Vorhersage verwendet. ",
        "Durch eine graphische App-Oberfläche ist eine geeignete Visualisierung vorhanden für den Benutzer.",
        html.Br(),
        "Außerdem wird der aktuelle Standort des Nutzers live angezeigt und bei Abwegen der Route, registriert das Programm dies und berechnet anhand der aktuellen Standortdaten eine neue Route. ",
        "Zusätzliche Informationen, wie von anderen Navigationsanbieter bekannt, wie Geschwindigkeit, ungefähre Gesamtzeit der Strecke und Gesamtentfernung werden dem Nutzer angezeigt für die jeweilige Route."]

            

def layout(**kwargs):
    return dbc.Container(children = [
    sidebar(),
    html.Div(html.P(text)),
    ],
    fluid = True, # remove the margins
    style={'padding': 0,
           "height": "98vh",
           "width": "100%"}, # removes ALL the margins
    className="bg-light", # background color
)


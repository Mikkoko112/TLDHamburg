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
                    path='/live',
                    title='Live: Traffic-Light Navigation',
                    name='Live: Traffic-Light Navigation')

#external CSS stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

def layout(**kwargs):
    return dbc.Container(children = [
    sidebar(),
    html.Div("Live"),
    ],
    fluid = True, # remove the margins
    style={'padding': 0,
           "height": "98vh",
           "width": "100%"}, # removes ALL the margins
    className="bg-light", # background color
)
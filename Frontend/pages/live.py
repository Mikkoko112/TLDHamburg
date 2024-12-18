import dash
from dash import dcc, html, no_update, ctx, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import dash_bootstrap_components as dbc

from tldhamburg.frontend import APIkeys
from tldhamburg.frontend import * # in __innit__.py __all__ = ["filename.py", "otherfile.py",...]

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

position = position.Position() # Create a position Object

# Main layout
def layout(**kwargs): 
    return dbc.Container(children = [
    navbar_live(),
    data_live(position)
    ],
    fluid = True, # remove the margins
    className="demo-live-container",
)

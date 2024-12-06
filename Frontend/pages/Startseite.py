import dash
#from dash import Dash, html, dcc 
import dash_bootstrap_components as dbc

from .components import sidebar
from .components import text

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
          

def layout(**kwargs):
    return dbc.Container(children = [
    sidebar(),
    text(),
    ],
    fluid = True, # remove the margins
    style={'padding': 0,
           "height": "98vh",
           "width": "100%"}, # removes ALL the margins
    className="bg-light", # background color
)


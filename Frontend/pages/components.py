import dash
from dash import html
import dash_bootstrap_components as dbc

def sidebar():
    return html.Div(
        dbc.Nav(
            [
                dbc.NavLink(
                    html.Div(page["name"], className="ms-2"),
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
            className="bg-light",
        )
    )

def headline():
    return dbc.Row([
        dbc.Col(html.H1("Real-Time Traffic Light Map"), className="text-center")
        ],
        style={"height": "6vh"}
        )


from threading import Timer
import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
from tldhamburg.frontend import * 

# external CSS stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

# initialize the app
app = Dash(__name__, external_stylesheets = external_stylesheets,use_pages=True)

# add the layout for the app
# dash.page_container considers the layout of the individual pages
app.layout = html.Div([
    dash.page_container
])

# Set the page title and description
app.title = "TrafficLightNavigation"
app.description = "Eine interaktive Karte mit optimalen Routen für einen bestimmten Start- und Zielort."

if __name__ == "__main__":
    Timer(1, open_browser.open_browser).start()
    app.run_server(debug=True, port=1222)
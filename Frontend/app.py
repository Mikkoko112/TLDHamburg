from threading import Timer
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from tldhamburg.frontend import * 


#external JavaScript files
external_scripts = []

#external CSS stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
]

app = Dash(__name__, external_stylesheets = external_stylesheets,use_pages=True)

app.layout = html.Div([
    dash.page_container
])

# Set the page title
app.title = "TrafficLightNavigation"
app.description = "An interactive map of optimal routes for a specific start and end location."

if __name__ == '__main__':
    Timer(1, open_browser.open_browser).start()
    app.run_server(debug=True, port=1222)
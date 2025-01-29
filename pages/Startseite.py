import dash
from dash import no_update, dcc, callback, ctx
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# import components for the page
from .components import headline
from .components import components_startseite

# register_page signalizes dash that it is a page for the app
dash.register_page(__name__,
                    path="/",
                    title="Startseite",
                    name="Startseite")

# Layout definition
def layout():
   return dbc.Container(children = [
    # Update and track the current window.location object
    dcc.Location(id="url", refresh=True),  
    # Include the headline
    headline(), 
    # Include cards and information texts
    components_startseite(), 
   ],
    fluid = True, # remove the margins
    className="startseite-container", 
)

"""
Decide to navigate to page demo or page live.
Input: the number of clicks of the left or right card
Output: The card which was clicked will have a lower opacity. 
If clicked twice in a row at the same card the page will change to the demo 
or live page.
"""
@callback(
    Output("url", "pathname"),
    Output("img-right-card","style"),
    Output("img-left-card", "style"),
    Output("link-right-card","n_clicks"),
    Output("link-left-card","n_clicks"),
    Input("link-right-card","n_clicks"),
    Input("link-left-card","n_clicks"),
   prevent_initial_call=True
)
def url_live(n_clicks_right,n_clicks_left):
    link_id = ctx.triggered_id
    if link_id == "link-right-card":
        if n_clicks_right>1:
            return "/live",no_update,no_update,no_update,no_update
        elif n_clicks_right:  
            return no_update,{"opacity": "0.4"},{"opacity": "1"},no_update,0
    elif link_id == "link-left-card":
        if n_clicks_left>1:
            return "/demo",no_update,no_update,no_update,no_update
        elif n_clicks_left:  
            return no_update,{"opacity": "1"},{"opacity": "0.4"},0,no_update    
    return no_update,no_update,no_update,no_update,no_update
   
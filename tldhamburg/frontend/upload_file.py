import os
import base64
from urllib.parse import quote as urlquote
from dash import html
import dash_bootstrap_components as dbc
from pathlib import Path

#cwd = Path.cwd() # current working directory
#parent = cwd.parent
UPLOAD_DIRECTORY = f"{Path.cwd()}/Frontend/app_uploaded_files"

#if not os.path.exists(UPLOAD_DIRECTORY):
#    os.makedirs(UPLOAD_DIRECTORY)

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


def file_load_link(filename):
    """Create a NavLink which you can click and select the file"""
    location = "/Frontend/app_uploaded_files/{}".format(urlquote(filename))
    #return  dbc.NavLink(filename, id="button-link", n_clicks=0)
    return 

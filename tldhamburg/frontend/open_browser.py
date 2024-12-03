import os
import webbrowser

def open_browser():
    # opens app in browser with address = IP
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')
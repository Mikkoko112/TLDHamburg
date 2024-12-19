import json
import time
from tldhamburg.backend.Things import Things
from pathlib import Path


def get_trafficlights(): # Nike ausbauen
    directory = f"{Path.cwd()}/Frontend/schnittstelle"
    with open(f"{directory}/trafficlights.geojson", "r") as f:
        data = json.load(f)
    return data

class Trafficlight:
    things_id = None            # things object
    _lat = None
    _lon = None
    object_type = None          # signal type

    status = None                


    def __init__(self, things_id, lat, lon, object_type):
        self.things_id = things_id
        self._lat = lat
        self._lon = lon
        self.object_type = object_type
        pass

    def get_coordinates(self, option=["latlon", "lonlat"]):
        if option == "latlon":
            return self._lat, self._lon
        if option == "lonlat":
            return self._lon, self._lat
        
    def set_status(self, status):
        self.status = status
        return status
        
    
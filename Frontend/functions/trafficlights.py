import json
import time
from functions import Things
from pathlib import Path

def get_trafficlights():
    cwd = Path.cwd()
    directory = f"{cwd}/schnittstelle"
    with open(f"{directory}/trafficlights.geojson", "r") as f:
        data = json.load(f)
    return data

class Trafficlight:
    thing = None             # things object
    _lat = None
    _lon = None
    way_point_idx = None    # 
    _color = None            
    _turns_green = None      # green prediction; time
    _turns_red = None        # red prediction; time


    def __init__(self, things_id, lat, lon, way_point_index):
        self.thing = Things([things_id])
        self._lat = lat
        self._lon = lon
        self.way_point_index = way_point_index
        pass

    def get_coordinates(self, option=["latlon", "lonlat"]):
        if option == "latlon":
            return self._lat, self._lon
        if option == "lonlat":
            return self._lon, self._lat
        
    def get_predictions(self):
        print("getting predictions...")
        pass

    def update(self):
        # checks if predictions are outdated
        if self._turns_green is not None:
            current_time = time.time()
            if self._turns_green <= current_time:
                self.get_predictions()
            if self._turns_red <= current_time:
                self.get_predictions()
        
        # gets color of traffic light
        
        pass
        
    
import json
from pathlib import Path

class Position:
    _lat = 0
    _lon = 0
    #navigating = bool
    def __init__(self):
        pass
        #self.navigating = False
        #directory = f"{Path.cwd()}/schnittstelle"
        #with open(f"{directory}/position.geojson", "r") as f:
        #    _file = json.load(f)
        #    self._lat, self._lon = _file["coordinates"]

    def set_pos(self, lat, lon):
        self._lat = lat
        self._lon = lon
        return self._lat, self._lon

    def set_coordinates(self, coordinates):
        if not isinstance(coordinates, (list, tuple)):
            raise ValueError("Input must be list or tuple (lat, lon).")
        if len(coordinates) != 2:
            raise ValueError("Input expected to be of length 2")
        self._lat, self._lon = coordinates
        return self._lat, self._lon

    def get_pos(self, latlon="latlon"):
        if latlon == "latlon":
            return self._lat, self._lon
        else:
            return self._lon, self._lat
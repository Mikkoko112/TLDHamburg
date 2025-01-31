import json
from pathlib import Path

class Position:
    """
    This class saves the coordinates of your location. It is currently in a very simple state - but: 
    Any position logic like e.g. smoothing positions if there are interrupances during navigation like in tunnels etc.
    shall be handled in this class, as Navigation() (to which this class is complementary) will work irrespective 
    of technical errors during position locating.
    """
    _lat = 0
    _lon = 0
    def __init__(self):
        pass

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
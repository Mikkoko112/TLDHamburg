import json
from pathlib import Path

class Position:
    _lat = 0
    _lon = 0
    navigating = bool
    def __init__(self):
        self.navigating = False
        directory = f"{Path.cwd()}/schnittstelle"
        with open(f"{directory}/position.geojson", "r") as f:
            _file = json.load(f)
            self._lat, self._lon = _file["coordinates"]

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

    def get_pos(self):
        return self._lat, self._lon

#Alternative: Positionsdaten in eine geojson-Datei schreiben

# def get_pos():
#     cwd = Path.cwd()
#     directory = f"{cwd}/schnittstelle"
#     with open(f"{directory}/position.geojson", "r") as f:
#         pos = json.load(f)
#     lat, lon = pos["coordinates"]
#     return [lat, lon]

# def set_pos(lat, lon):
#     cwd = Path.cwd()
#     directory = f"{cwd}/schnittstelle"

#     with open(f"{directory}/position.geojson", "r") as f:
#         data = json.load(f)

#     data["coordinates"] = [lat, lon]

#     with open(f"{directory}/position.geojson", "w") as f:
#         json.dump(data)

#     pass
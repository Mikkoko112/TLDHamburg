"""Data Models for Routing implementation"""

from dataclasses import dataclass
import xml.etree.ElementTree as ET
import math
import requests

TOLERANCE = 0.0000001


def minimum_distance_node(to, candidates):
    """Find OSM the node in a list which has the minimum distance
    to an ORS node"""
    min_node = None
    min_distance = float("inf")

    for node in candidates:
        _id = int(node.attrib["id"])
        _lat = float(node.attrib["lat"])
        _lon = float(node.attrib["lon"])

        distance = math.dist((to.lat, to.lon), (_lat, _lon))

        if distance < min_distance:
            min_distance = distance
            min_node = OSMNode(_id, _lat, _lon)

    return min_node


@dataclass
class ORSNode:
    """Class used to represent a Node in ORS"""

    id: int
    lat: float
    lon: float

    def __matmul__(self, other) -> float:
        return self.lat * other.lat + self.lon * other.lon

    def __sub__(self, other):
        return ORSNode(id=-9999, lat=self.lat - other.lat, lon=self.lon - other.lon)

    def __abs__(self):
        return math.dist((0, 0), (self.lat, self.lon))


@dataclass
class OSMNode:
    """Class used to represent a Node in OSM"""

    id: int
    lat: float
    lon: float

    @classmethod
    def from_ors(cls, n_from: ORSNode):
        """Generate an OSM node from an ORS node"""
        bbox_limits = [
            n_from.lon - TOLERANCE,
            n_from.lat - TOLERANCE,
            n_from.lon + TOLERANCE,
            n_from.lat + TOLERANCE,
        ]
        call = requests.get(
            "https://www.openstreetmap.org/api/0.6/map?bbox="
            + ",".join(str(x) for x in bbox_limits),
            timeout=5,
        )
        xml_data = ET.fromstring(call.text)

        return minimum_distance_node(n_from, xml_data.iter("node"))

    def __matmul__(self, other) -> float:
        return self.lat * other.lat + self.lon * other.lon

    def __sub__(self, other):
        return OSMNode(id=-9999, lat=self.lat - other.lat, lon=self.lon - other.lon)

    def __abs__(self):
        return math.dist((0, 0), (self.lat, self.lon))

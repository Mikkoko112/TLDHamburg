#!/usr/bin/env python3
from timeit import default_timer as timer
import igraph
import math


def find_closest_node(lat: int, lon: int, G: igraph.Graph):
    minimum_distance = math.inf
    minimum_node = None
    for node in G.vs:
        distance = math.sqrt((lat-node["lat"])**2+(lon-node["lon"])**2)
        if distance >= minimum_distance:
            continue
        minimum_distance = distance
        minimum_node = node["nodeid"]
    return minimum_node

if __name__ == "__main__":
    lat = 53.4704513569805
    lon = 9.91552925129873
    G = igraph.load("../data/hamburg.gml")
    start = timer()
    print(f"Closest node to {lat}, {lon}")
    print(find_closest_node(lat, lon, G))
    end = timer()
    print(f"This took {end-start} seconds.")

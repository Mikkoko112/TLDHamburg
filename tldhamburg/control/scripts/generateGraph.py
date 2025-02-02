#!/usr/bin/env python3

import igraph
import pyrosm

# OSM Data extracts can be downloaded from https://download.geofabrik.de/
# They come as .pbf files and may be restricted to continents, nations, states and cities
# depending on location. (some locations offer greater sub-region resolution than others.)
# The name of the input file must be adjusted below.

INPUT_DATA = "../data/hamburg-latest.osm.pbf"

if __name__ == "__main__":
    osm = pyrosm.OSM(INPUT_DATA)
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    G = osm.to_graph(nodes, edges)
    G.write_gml("../data/hamburg.gml")

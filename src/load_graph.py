import igraph

def nodeid_to_latlon(G: igraph.GraphBase, node_id: int) -> (float, float):
    vertex = G.vs.select(node_id)
    return vertex["lat"], vertex["lon"]

if __name__ == "__main__":
    G = igraph.load("../data/hamburg.gml")
    print("is graph directed:", G.is_directed())
    print(f"Shortest path from [{nodeid_to_latlon(G, 1)}] to [{nodeid_to_latlon(G, 3)}]")
    print("[")
    for node in G.get_shortest_path(1,3):
        print(nodeid_to_latlon(G, node))
    print("]")

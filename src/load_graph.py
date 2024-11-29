from timeit import default_timer as timer
import igraph
import json

def node_to_latlon(node) -> (float, float):
    return node["lat"], node["lon"]

G = igraph.load("../data/hamburg.gml")
print("is graph directed:", G.is_directed())


def main():
    node_start = G.vs.select(1)
    node_end = G.vs.select(3)
    print(f"Shortest path from [{node_to_latlon(node_start)}] to [{node_to_latlon(node_end)}]")
    print("[")
    start = timer()
    last_node = None
    last_edge = None
    last_street_name = ""
    for node_id in G.get_shortest_path(1,3):
        node = G.vs.select(node_id)
        #print(node_to_latlon(node))
        if last_node is None:
            last_node = node
            continue
        edge_id = G.get_eid(int(last_node['nodeid'][0]), int(node['nodeid'][0]))
        #print(f"Via edge {edge_id}")
        edge = G.es.select(edge_id)
        edge_attrs = json.loads(edge["tags"][0])
        #print(edge["name"])
        if last_edge is None:
            last_edge = edge
            last_street_name = edge['name'][0]
            last_node = node
            continue
        for key in edge_attrs:
            if "turn" in key:
                #print(edge_attrs)
                break
        if last_street_name != edge["name"][0] and edge['name'][0] != 'None':
            print(last_street_name, edge['name'][0])
        last_node = node
        last_edge = edge
        if edge['name'][0] != 'None':
            last_street_name = edge['name'][0]
    print("]")
    end = timer()
    print(f"Calculating the route and its coordinates took {end-start} seconds."

if __name__ == "__main__":
    main()

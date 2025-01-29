import igraph
from math import inf
'''
This file was made to pro

'''

remove = [
    "access", 
    "area" ,
    "bicycle" ,
    "bicycleroad" ,
    "bridge" ,
    "cycleway" ,
    "estwidth" ,
    "foot" ,
    "footway" ,
    "width" ,
    "surface",
    "smoothness" ,
    "sidewalk",
    "intref" ,
    "lit",
    "segregated",
    "turn",
    "timestamp",
    "version",
    "tags",
    "psv",
    "tracktype",
    "tunnel",
    "useq",
    "vseq"
]
removeSecond=[
    "busway",
    "highway",
    "lanes",
    "motorcar",
    "motorroad",
    "motorvehicle",
    "overtaking",
    "ref",
    "junction",
    "passingplaces",
    "service"
]
removeVs = [
    "changeset",
    "visible",
    "version",
    "timestamp"
]

def getBoundingBoxOfGraph(graph):
    
    
    minX,maxX = inf,0
    minY,maxY = inf,0
    
    for vertex in graph.vs:
        if vertex["lat"] < minX:
            minX = vertex["lat"]
        
        if vertex["lat"] > maxX:
            maxX = vertex["lat"]
        
        if vertex["lon"] < minY:
            minY = vertex["lon"]
        
        if vertex["lon"] > maxY:
            maxY = vertex["lon"]
        

    # Compute bounding box
    bounding_box = {
        "x_min": minX,
        "x_max": maxX,
        "y_min": minY,
        "y_max": maxY,
    }

    return bounding_box


if __name__ == "__main__":
    graph = igraph.load("shHamburg.gml")
    print("Graph loaded")
    print(getBoundingBoxOfGraph(graph))
    exit()
    for rm in removeSecond:
        del graph.es[rm]

    #for rm in removeVs:
    #    del graph.vs[rm]
    
    graph.write_gml("shHamburgRemoveSecond.gml")
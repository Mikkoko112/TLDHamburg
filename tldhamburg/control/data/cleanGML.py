import igraph

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

removeVs = [
    "changeset",
    "visible",
    "version",
    "timestamp"
]

if __name__ == "__main__":
    graph = igraph.load("hamburg.gml")
    for rm in remove:
        del graph.es[rm]

    for rm in removeVs:
        del graph.vs[rm]
    
    graph.write_gml("shHamburg.gml")
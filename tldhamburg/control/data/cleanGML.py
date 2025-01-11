import igraph

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


if __name__ == "__main__":
    graph = igraph.load("shHamburg.gml")
    for rm in removeSecond:
        del graph.es[rm]

    #for rm in removeVs:
    #    del graph.vs[rm]
    
    graph.write_gml("shHamburgRemoveSecond.gml")
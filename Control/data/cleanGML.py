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
"lit"
]

secondRemove = [
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
    graph = igraph.load("shortshortendHamburg.gml")
    for rm in secondRemove:
        print(graph.es.attributes())
        del graph.es[rm]
        print(graph.es.attributes())

    graph.write_gml("extrashortshortendHamburg.gml")
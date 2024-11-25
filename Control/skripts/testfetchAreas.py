#!/usr/bin/env python3
import json
import fetchAreas


def getWrongSquares(coords:dict,coordsBase:dict)->dict:
    out = dict()
    for name,coord in coords.items():
        if len(coord) != 4:
            out[name] = coordsBase[name]
    for name,coord in coordsBase.items():
        if not name in coords:
            out[name] = coord
        
    return out

def testRoundValue(options:dict):
    modif = options["modif"]
    input = [1/(modif+1),1/modif]
    out   = [0,1/modif]

def checkLength(options:dict):
    
    with open(f"..{options["importantData"]["allFetchAreas"]}","r") as file:
        coordsBase = json.load(file)

    with open(f"..{options["importantData"]["holeData"]}","r") as file:
        coords = json.load(file)

    print(len(coordsBase),len(coords))

    out = getWrongSquares(coords,coordsBase)
    
    with open("missingData.json","w") as file:
        json.dump(out,file,indent=4)
    if (len(out)) > 0: 
        print(f"Test failed there are {len(out)} missing or corruptet squares.")
        exit(1)
    print("Area data is complete")


if __name__ == "__main__":
    with open("../optionsfile.json","r") as file:
        options = json.load(file)
    checkLength(options)

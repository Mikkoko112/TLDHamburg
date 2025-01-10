#!/usr/bin/env python3
import json
from tldhamburg.control.scripts.fetchAreas import roundValues,getNotes

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
    print("Round test started.")
    modif = options["modif"]
    inp = [[1/(modif+1),1/modif],[1/(modif+1),1/modif]]
    out   = [[0.0,1/modif],[1/modif,1/modif]]
    values = roundValues(inp,modif)
    if not all([True if ou == val else False for val,ou in zip(values,out)]):
        print("The round function does not work as it should be.")
        exit()
    print("Round test finished")

def testGetNotes(options:dict):
    print("Fetchtest started.")
    coords = [
            [
                9.9489717,
                53.5462321
            ],
            [
                9.9561542,
                53.5588747
            ]
        ]
    area = getNotes(coords)
    if len(area) == 1:
        print("Did not retreat the pulled Data.")
        exit()
    print("Fetchtest finished.")

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
        print(f"Test failed there are {len(out)} missing or corrupted squares.")
        exit(1)
    print("Area data is complete")


if __name__ == "__main__":
    with open("../optionsfile.json","r") as file:
        options = json.load(file)
    checkLength(options)
    testRoundValue(options)
    #testNode(options)

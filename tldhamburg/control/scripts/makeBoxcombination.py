#!/usr/bin/env python3
from tldhamburg.control.scripts.makeFetchSquares import findSmallestAndLargestCoord
import json
from shapely.geometry import box

def combineAreas(areas:dict)->dict:
    out = {}
    for name, values in areas.items():
        if len(values) != 3:
            values.append(True)
            listOfName = values[1]
            coord1 = values[0]
            rect1 = box(coord1[0][0],coord1[0][1],coord1[1][0],coord1[1][1])
            #print(rect1)
            for name2,values2 in areas.items(): 
                if len(values2) != 3 or True:
                    coord2 = values2[0]
                    rect2 = box(coord2[0][0],coord2[0][1],coord2[1][0],coord2[1][1])
                    if rect1.intersects(rect2):
                        
                        values2.append(True)
                        listOfName += values2[1]
            coordMinMax = findSmallestAndLargestCoord(listOfName)
            out[name] = [coordMinMax,listOfName]
    return out



def runCombination()->None:
    with open("../data/conjunctions.json","r") as file:
        coords = json.load(file)
    print(len(coords))
    areas = combineAreas(coords)
    print(len(areas))
    with open("../data/conjunctionsJoint.json","w") as file:
        json.dump(areas, file, indent=4)


if __name__ == "__main__":
    runCombination()

#!/usr/bin/env python3
from makeFetchSquares import findSmallestAndLargestCoord
import json
from shapely.geometry import box

def combineAreas(areas:dict)->dict:
    '''
    Input 
        <- areas = ... This is the loaded area data.
        
    Output
        -> The output are areas that are now combined, when they interesect.
    
    This script converts all areas into boxes that are then ckecked for 
    intersection.
    '''
    
    out = {}
    for name, values in areas.items():
        if len(values) != 3:
        
            values.append(True)
            listOfName = values[1]
            coord1 = values[0]
            rect1 = box(coord1[0][0],coord1[0][1],coord1[1][0],coord1[1][1])
        
            for name2,values2 in areas.items(): 
                if len(values2) != 3 or True:
                    coord2 = values2[0]
                    rect2 = box(coord2[0][0],coord2[0][1],coord2[1][0],coord2[1][1])
                    if rect1.intersects(rect2):
                        
                        values2.append(True)
                        listOfName += values2[1]

            coordMinMax = findSmallestAndLargestCoord(listOfName)
            cleanedListOfName = cleanSimilar(listOfName)
            out[name] = [coordMinMax,cleanedListOfName]
            nameLength = len([name for name,coords in cleanedListOfName])
            shnameLength = len(set([name for name,coords in cleanedListOfName]))
            if not nameLength == shnameLength:
                print(name,nameLength,shnameLength,nameLength == shnameLength)
    
    return out

def cleanSimilar(listOfName:list)->list:
    '''
    Input
        <- listOfName = [str,...] This is a list of all primary signals per area

    Output
        -> The output is the list of primary signals that are distinct to 
            each other.
    
    '''
    
    
    out = []
    newNames = []
    for name,coords in listOfName:
        if not name in newNames:
            newNames.append(name)
            out.append([
                name,
                coords
            ])
    return out


def runCombination()->None:
    '''
    This program is used only in data formation and is not interactiv. 
    Rerun this if the concuntionsJoint file is missing.
    '''


    with open("../data/conjunctionsMean.json","r") as file:
        coords = json.load(file)
    print(len(coords))
    areas = combineAreas(coords)
    print(len(areas))
    with open("../data/conjunctionsJoint.json","w") as file:
        json.dump(areas, file, indent=4)


if __name__ == "__main__":
    runCombination()

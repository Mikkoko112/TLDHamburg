#!/usr/bin/env python3
import json 

def testCountOfThings():
    with open("../data/cleanedCoors.json","r") as file:
        originalData = json.load(file)
    with open("../data/conjunctions.json","r") as file:
        jointData = json.load(file)

    leftoutThings = []

    thingsFromJoint = {}
    for nameSquare,list in jointData.items():
        listofNames = list[1]
        for name,coord in listofNames:
            thingsFromJoint[name] = coord
    
    for name,thing in originalData.items():
        if not(name in thingsFromJoint):
            leftoutThings.append(name)

    print(len(leftoutThings))
    print(leftoutThings)

def testMeanAndOrig():
    with open("../data/thingsLoc.json","r") as file:
        originalData = json.load(file)
    with open("../data/cleanedCoors.json","r") as file:
        meanData = json.load(file)

    leftoutThings = []

    for name,thing in originalData.items():
        if not(name in meanData):
            leftoutThings.append(name)
    print(len(leftoutThings))
    print(leftoutThings)


if __name__ == "__main__":
    testMeanAndOrig()

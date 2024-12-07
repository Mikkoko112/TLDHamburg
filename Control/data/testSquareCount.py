#!/usr/bin/env python3
import json 

def testCountOfThings(options:dict):
    with open(f"..{options["importantData"]["thingsLoc"]}","r") as file:
        originalData = json.load(file)
    with open(f"..{options["importantData"]["conjunctionData"]}","r") as file:
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

    if len(leftoutThings) > 1:
        print("Test failt. Recompile Data")
        exit(1)

    
    print(len(leftoutThings))
    print(leftoutThings)

def testMeanAndOrig(options:dict):
    with open(f"..{options["importantData"]["thingsLoc"]}","r") as file:
        originalData = json.load(file)
    with open(f"..{options["importantData"]["meanValueData"]}","r") as file:
        meanData = json.load(file)

    leftoutThings = []

    for name,thing in originalData.items():
        if not(name in meanData):
            leftoutThings.append(name)
    if len(leftoutThings) > 1: 
        print("Test failt. Recompile Data")
        exit(1)
    print(len(leftoutThings))
    print(leftoutThings)


if __name__ == "__main__":
    with open("../optionsfile.json","r") as file:
        options = json.load(file)
    testMeanAndOrig(options)
    testCountOfThings(options)
    print("SquareCountTest passd")


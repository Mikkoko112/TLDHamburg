#!/usr/bin/env python3
import json 

def testCountOfThings(options:dict):
    with open(f"..{options["importantData"]["thingsLoc"]}","r") as file:
        originalData = json.load(file)
    # with open(f"..{options["importantData"]["conjunctionData"]}","r") as file:
    #     jointData = json.load(file)
    print("conjTest")
    with open("conjunctionsJoint.json","r") as file: 
        jointData = json.load(file)

    keys = originalData.keys()
    conjPimList= []
    conjCount = 0
    for conj,primList in jointData.items():
        for prim in primList[1]:
            if conj == "22472":
                conjCount +=1
            conjPimList.append(prim[0])

    print("ConjCount",conjCount)

    left = keys-conjPimList

    if len(left) > 1:
        print("Test failt. Recompile Data")
        exit(1)

    print(len(keys),len(conjPimList))
    print(len(left))
    print(left)

def testMeanAndOrig(options:dict):
    with open(f"..{options["importantData"]["thingsLoc"]}","r") as file:
        originalData = json.load(file)
    with open(f"..{options["importantData"]["meanValueData"]}","r") as file:
        meanData = json.load(file)

    
    keys = meanData.keys()
    keysOrgig = originalData.keys()
    print(keysOrgig-keys)
    leftoutThings = keysOrgig-keys

    if len(leftoutThings) > 1: 
        print("Test failt. Recompile Data")
        exit(1)
    print(len(leftoutThings))
    print(leftoutThings)

def checkPrimarySignalCountOfDict(options:dict):
    with open(f"..{options["importantData"]["thingsLoc"]}","r") as file:
        originalData = json.load(file)
    with open(f"conjunctionDict.json","r") as file:
        conjDict = json.load(file)
    
    leftoutThings = []
    keys = originalData.keys()
    for conj, item in conjDict.items():
        print(conj)
        
        for thId in item["trafficLights"]: 
            #print(thId,end=" ")
            leftoutThings.append(thId)
    
    left = keys-leftoutThings
    
    
    print(left)
    print(len(left))     

def testVectorGenerator(options:dict):
    with open(f"vectorizationOnMeanPointInvert.json","r") as file:
        vec = json.load(file)
    with open(f"..{options["importantData"]["thingsLoc"]}","r") as file:
        originalData = json.load(file)

    missing = originalData.keys() - vec.keys()
    print(missing)
    print(len(missing))

def testCleanedCoordAverage(options:dict):
    with open(f"cleanedCoorsAverage.json","r") as file:
        points = json.load(file)

    with open(f"..{options["importantData"]["thingsLoc"]}","r") as file:
        originalData = json.load(file) 

    missing = originalData.keys() - points.keys()
    print(missing)
    print(len(missing))
    print(len(originalData.keys()),len(points.keys()))


if __name__ == "__main__":
    with open("../optionsfile.json","r") as file:
        options = json.load(file)
    #testMeanAndOrig(options)
    #testCountOfThings(options)
    checkPrimarySignalCountOfDict(options)
    #testVectorGenerator(options)
    #testCleanedCoordAverage(options)
    print("SquareCountTest passd")


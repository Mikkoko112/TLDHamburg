#!/usr/bin/env python3
import json
import os
import testSquareCount

def testIfDataIsThere():
    with open("tldhamburg/control/optionsfile.json","r") as file:
        options = json.load(file)
    print("Datatest started")
    filesInData = os.listdir("tldhamburg/control/data")
    for fileName,path in options["importantData"].items():
        if not path.split("/")[2] in filesInData:
            print("{} is missing at locataion:{}".format(fileName,path))
            exit(1)
    print("Datatest passed")

if __name__ == "__main__":
    
    testIfDataIsThere()

    
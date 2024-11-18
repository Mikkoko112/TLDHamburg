#!/usr/bin/env python3
import json
import os


def testIfDataIsThere():
    with open("../optionsfile.json","r") as file:
        options = json.load(file)
    filesInData = os.listdir(".")
    for fileName,path in options["importantData"].items():
        if not path in filesInData:
            print("{} is missing at locataion:{}".format(fileName,path))
            exit(1)

if __name__ == "__main__":
    testIfDataIsThere()
    
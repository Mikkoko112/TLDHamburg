#!/usr/bin/env python3

from tldhamburg.control.routeplanning.routing import inbound,inDegreeOffset
from math import degrees

def testInbound():
    print("Bounding Test started")
    bound = [
        [-1,-1],
        [1,1]
    ]
    testCases = [
        [[0,0],True],
        [[-2,0],False],
        [[1,1],True],
        [[-1,1],True],
        [[-1.1,1],False]
    ]

    for point,out in testCases:
        if not inbound(bound,point) == out: 
            print(f"Bounding test failt at point {point}")
            exit(1)
    print("Boudning test passed")

def testDegree():
    testValues = [
        [[30,50],True],
        [[10,30],True],
        [[10,36],False],
        [[350,10],True],
        [[10,359],True],
        [[50,80],False]
    ]

    for degers,val in testValues:
        if not inDegreeOffset(degers[0],degers[1]) == val:
            print(f"Degree function has a bug at {degers}")
            exit(1)
    print("Degree test passed")





if __name__ == "__main__":
    testInbound()
    testDegree()
    

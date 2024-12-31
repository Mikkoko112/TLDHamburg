#!/usr/bin/env python3

from VectorGenerator import generateVector,getCentroid,getDegree
from math import radians,sin,cos,degrees,sqrt

def testVectorGeneration(): #i need to implement way more test cases here
    print("Vektorgenerator test started")
    print("-test norming")
    main = [0,0]
    centroid = [[8,
            9]]
    vec = generateVektor(main,centroid)
    length = vec[0]**2+vec[1]**2
    if length >= 1+0.01 or  length <= 1-0.01:
        print("Normalisation did not work.")
        exit(1)
    print("-passed normation test")
    main = [0.0,100.0]
    centroid = [[0.0,1.0]]
    out = [0,1]
    vec = generateVektor(main,centroid)
    if not all(ve == ou for ve,ou in zip(vec,out)):
        print("There is something wrong with the vekt Generator")
        exit(1)
    print("Vektorgenerator test passed")

def testCentroid():
    testcases = [
        [[[0,1],[0,1]] , [0,1]],
        [[[2,0],[0,2]] , [1,1]]
    ]

    for inp,out in testcases:
        if not all([ou == test for ou,test in zip(out,getCentroid(inp))]):
            print("There is something wrong with the centroid generator.")
            print(f"Divergent values at: input {inp} and out {out}")
            exit(1)

    print("Centroid test passed.")
    
def testDegree():
    print("Degree test started")
        #[sin,cos]
    testVec = [[0,1],[1,0],[0,-1],[-1,0],[1/2,sqrt(3)/2]]
    out = [0,90,180,270,30]
    for vec,ou in zip(testVec,out):
        if not round(degrees(getDegree(vec))) == ou:
            print("The Degree function is not working.")
            exit(1)
    
    print("Degree test passed")


if __name__ == "__main__":
    testVectorGeneration()
    testCentroid()
    testDegree()
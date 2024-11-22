#!/usr/bin/env python3
import pickle, os
import json

cwd = os.getcwd()

locations_file = cwd + "/things_locations.pkl"
with open(locations_file, "rb") as file:
    things_locations = pickle.load(file)
    
with open("thingsLoc.json","w") as file:
    json.dump(things_locations,file,indent=4)


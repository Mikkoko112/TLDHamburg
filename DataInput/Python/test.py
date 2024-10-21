import requests
import json

test_coords = [1,2]

def switch_coords(input_list):
    temp = input_list[0]
    input_list[0] = input_list[1]
    input_list[1] = temp

switch_coords(test_coords)

print(test_coords)
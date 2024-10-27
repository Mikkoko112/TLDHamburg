import pickle, os

cwd = os.getcwd()

locations_file = cwd + "/DataInput/Python/data/things_no_locations.pkl"
with open(locations_file, "rb") as file:
    things_locations = pickle.load(file)

print(things_locations)

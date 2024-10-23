import pickle


locations_file = "/home/teo/Repositories/ci-s-projekt-2024-mikko/DataInput/Python/data/things_no_locations.pkl"
with open(locations_file, "rb") as file:
    things_locations = pickle.load(file)

print(len(things_locations))

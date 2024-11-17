#!/usr/bin/env python3

from tldhamburg.backend.DataFetcher import DataFetcher
from tldhamburg.backend.DBMaintainer import DBMaintainer

dfetcher = DataFetcher()
params = {"$expand": "Datastreams"}
dfetcher.fetch_data(endpoint="Things", params=params)
print("Fetching data is completed successfully!")
# Iterate over each fetched data entry to insert into the database
for data in dfetcher.data:
    # =========================
    # Process and Insert into Things Table
    # =========================
    thing_id = int(data.get("@iot.id"))
    # Retrieve the properties dictionary
    # Extract connectionID and trafficLightsID, defaulting to 0 if missing
    properties = data.get("properties")
    connection_id = int(properties.get("connectionID", 0))
    traffic_lights_id = int(properties.get("trafficLightsID", 0))

    things_data = [
        (
            thing_id,
            connection_id,
            traffic_lights_id,
        )
    ]
    DBMaintainer.insert_things(things_data)

    # =========================
    # Process and Insert into Datastreams Table
    # =========================
    # Retrieve the list of Datastreams associated with the Thing
    datastreams = data.get("Datastreams")
    # Initialize a dictionary to hold Datastreams data with
    # the associated Thing ID
    dstreams_data = {"thingID": thing_id}
    # Iterate through each Datastream to extract relevant information
    # if datastreams are available
    for datastream in datastreams:
        if "properties" in datastream:
            # Extract the layer name from the Datastream properties
            layer_name = datastream["properties"].get("layerName")

            if layer_name == "bus_pre-request_point":
                layer_name = "bus_pre_request_point"
            dstreams_data[layer_name] = int(datastream["@iot.id"])
    DBMaintainer.insert_datastreams([dstreams_data])

print("Database update is completed successfully!")

import requests
import json

class DataStream():
    def __init__(self):
        #self.API_endpoint = "https://tld.iot.hamburg.de/v1.0/Datastreams?$filter=properties/layerName+eq+'primary_signal'+and+Thing/properties/trafficLightsID+eq+'1556'"
        self.API_endpoint = "https://tld.iot.hamburg.de/v1.1/Datastreams?$filter=properties/layerName eq 'primary_signal'&$top=1000"

        self.data = None

    def get_data(self):
        response = requests.get(self.API_endpoint)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
        else:
            data = response.json()
            self.data = data

    def get_ID_by_coordinates(self,coordinates):
        # Input: Type
        # coordinates: 2-Tuple (x_coordinate,y_coordinate)
        return

    def print_json(self):
        if not self.data:
            print("No data collected yet")
        else:
            print(json.dumps(self.data, indent=4))


            
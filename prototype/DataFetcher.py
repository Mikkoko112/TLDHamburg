import requests
import json
import pickle
import shapely
import time

class DataFetcher():
    BASE_URL = "https://tld.iot.hamburg.de/v1.1/"
    """---------------------------------------------------------------------------------------------
    class structure for fetching Traffic Light Data from IoT Hamburg. 
    TLD IoT Hamburg is based on the OGC SensorThingsAPI.
    More Information on "https://docs.ogc.org/is/18-088/18-088.html"
    ---------------------------------------------------------------------------------------------"""
    def __init__(self):
        self.data = None

    def fetch_data_deprecated(self,endpoint="Datastreams",params={}):
        """-----------------------------------------------------------------------------------------
        Info:
        fetch traffic light data from IoT Hamburg.
        IoT Hamburg API returns at most 1000 entries per GET request, even if top parameter is
        set higher. It is most efficient top set the top parameter to 1000 if needed so minimal
        time consuming GET requests are send. 3 cases distinctions are made for a "top" parameter
        of below 1000, over 1000 or not set.
        
        Parameters:
        - endpoint (str):   Defines which type of Entity to Query from the API
            Available options:  'Things', 'Datastreams', 'Observations', 'FeatureOfInterests',
                                'Locations', 'HistoricalLocations', 'Sensors', 'ObservedProperties'
                            In Addition, Entities can be accessed directly by their id, e.g.
                            'Thing(123)' as well as their sublinks e.g. 'Thing(123)/Locations'
        
        - params (dict):    Defines the search commands for the Query
            Available options:  '$filter', '$expand', '$top', '$orderby', '$select', '$count'

        Examples:
            To be added later
        -----------------------------------------------------------------------------------------"""
        full_url = self.BASE_URL + endpoint

        #get all entries if no top parameter is set
        if not "$top" in params:
            #add max $top parameter so the max amount of values are fetched per page
            #significantly reduces fetch times, as API GET requests are slow
            params["$top"] = 1000
            response = requests.get(full_url,params=params)
            if response.status_code != 200: #exit data fetching if request failed
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return
            #only if a Entity is accessed directly e.g. Things(1), there is no value key
            if not "value" in response.json():
                self.data = response.json()
                return
            fetched_data = response.json().get("value",[])
            all_data = list()
            all_data.extend(fetched_data)
            #repeatedly fetch next page of results until last one is reached
            while True:
                next_link = response.json().get("@iot.nextLink")
                if not next_link: #break if last page is reached
                    break
                response = requests.get(next_link)
                if response.status_code != 200: #exit data fetching if request failed
                    print(f"Failed to fetch data. Status code: {response.status_code}")
                    return
                fetched_data = response.json().get("value",[])
                all_data.extend(fetched_data)
            
            self.data = all_data
            return
        
        #get top x entries over multiple pages if top param exceeds 1000
        elif params["$top"] > 1000:
            entries_fetched = 0
            response = requests.get(full_url,params=params)
            if response.status_code != 200: #exit data fetching if request failed
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return
            #only if a Entity is accessed directly e.g. Things(1), there is no value key
            if "value" in response.json():
                fetched_data = response.json().get("value",[])
            else:
                self.data = response.json()
                return
            all_data = list()
            all_data.extend(fetched_data)
            entries_fetched += 1000
            #repeatedly fetch next page of results until last one is reached
            while True:
                next_link = response.json().get("@iot.nextLink")
                if not next_link: #break if last page is reached
                    break
                response = requests.get(next_link)
                if response.status_code != 200: #exit data fetching if request failed
                    print(f"Failed to fetch data. Status code: {response.status_code}")
                    return
                fetched_data = response.json().get("value",[])
                if params["$top"] - entries_fetched < 1000: #exit if last necassary page is reached
                    all_data.extend(fetched_data[:params["$top"]%1000])
                    break
                all_data.extend(fetched_data)
                entries_fetched += 1000
            
            self.data = all_data
            return

        #get top x entries in one page if top param is under or equal to 1000
        else:
            response = requests.get(full_url,params=params)
            if response.status_code != 200: #exit data fetching if request failed
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return
            #only if a Entity is accessed directly e.g. Things(1), there is no value key
            if "value" in response.json():
                fetched_data = response.json().get("value",[])
            else:
                self.data = response.json()
                return
            fetched_data = response.json().get("value",[])
            self.data = fetched_data

    def fetch_data(self,endpoint="Datastreams",params={}):
        next_request_link = self.BASE_URL + endpoint
        entries_to_fetch = float('inf')
        if "$top" in params:
            entries_to_fetch = params["$top"]
        all_data = list()
        entries_fetched = 0
        while True:
            response = requests.get(next_request_link,params=params)

            if response.status_code != 200: #exit data fetching if request failed
                raise ValueError(f"Failed to fetch data. Status code: {response.status_code}")
            
            if not "value" in response.json(): #save json directly, if entity is accessed directly
                all_data.append(response.json())
                break

            fetched_data = response.json().get("value",[])

            if entries_to_fetch - entries_fetched < 1000: #exit if last necassary page is reached
                all_data.extend(fetched_data[:entries_to_fetch%1000])
                break

            all_data.extend(fetched_data)
            entries_fetched += len(fetched_data)
            next_request_link = response.json().get("@iot.nextLink")

            if not next_request_link: #break if last page is reached
                break

        self.data = all_data
        
    def get_data(self):
        if not self.data:
            raise ValueError("No data fetched yet")
        return self.data
    
    def get_Datastream_id_by_coordinates(self,coordinates,error):
        # Input: Type
        # coordinates: list [x_coord,y_coord]

        if coordinates[0] > coordinates[1]:#switch coords if they are given in wrong orientation
            temp = coordinates[0]
            coordinates[0] = coordinates[1]
            coordinates[1] = temp

        with open("datastreams_id-observedArea.pkl", "rb") as file:
            data = pickle.load(file)
        
        all_matched_Datastreams_ids = list()
        reference_point = shapely.geometry.Point(coordinates[0],coordinates[1])
        for entry in data:
            if not "observedArea" in entry:
                continue
            geoJSON_observedArea = shapely.geometry.shape(entry["observedArea"])
            distance = reference_point.distance(geoJSON_observedArea)
            if distance < error:
                if not "@iot.id" in entry:
                    print("whoops")
                datastream_id = entry["@iot.id"]
                all_matched_Datastreams_ids.append(datastream_id)
        return all_matched_Datastreams_ids

    def get_live_Observations_for_Datastream_id(self,id):
        endpoint = f"Datastreams({id})"
        params = {
            "$expand" : "Observations($orderby=phenomenonTime desc;$top=1;$select=id,result,phenomenonTime)"
        }
        self.fetch_data(endpoint,params)
        print(f"current Status: {self.data["Observations"][0]["result"]}\t at Timestamp: {self.data["Observations"][0]["phenomenonTime"]}")
        last_Observation_id = self.data["Observations"][0]["@iot.id"]
        while True:
            time.sleep(1)
            self.fetch_data(endpoint,params)
            if last_Observation_id == self.data["Observations"][0]["@iot.id"]:
                continue
            last_Observation_id = self.data["Observations"][0]["@iot.id"]
            print(f"current Status: {self.data["Observations"][0]["result"]}\t at Timestamp: {self.data["Observations"][0]["phenomenonTime"]}")
            

    def print_raw_data(self):
        if not self.data:
            raise ValueError("No data fetched yet")
        print(json.dumps(self.data, indent=4))
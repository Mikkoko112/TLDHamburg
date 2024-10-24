import requests
import json

class DataFetcher():
    """---------------------------------------------------------------------------------------------
    class structure for fetching Traffic Light Data from IoT Hamburg. 
    TLD IoT Hamburg is based on the OGC SensorThingsAPI.
    More Information on "https://docs.ogc.org/is/18-088/18-088.html"
    ---------------------------------------------------------------------------------------------"""
    def __init__(self):
        self.base_url = "https://tld.iot.hamburg.de/v1.1/"
        self.data = None

    def fetch_data(self,endpoint="Datastreams",params={}):
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
        full_url = self.base_url + endpoint

        #get all entries if no top parameter is set
        if not "$top" in params:
            print("hi")
            #add max $top parameter so the max amount of values are fetched per page
            #significantly reduces fetch times, as API GET requests are slow
            params["$top"] = 1000
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
        elif params["top"] > 1000:
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

    def get_data(self):
        return self.data
    
    def get_ID_by_coordinates(self,coordinates):
        # Input: Type
        # coordinates: 2-Tuple (x_coordinate,y_coordinate)
        return

    def print_raw_data(self):
        if not self.data:
            print("No data collected yet")
        else:
            print(json.dumps(self.data, indent=4))


            
import requests
import json
import time
import math
from concurrent.futures import ThreadPoolExecutor


class DataFetcher:
    BASE_URL = "https://tld.iot.hamburg.de/v1.1/"
    """---------------------------------------------------------------------------------------------
    class structure for fetching Traffic Light Data from IoT Hamburg. 
    TLD IoT Hamburg is based on the OGC SensorThingsAPI.
    More Information on "https://docs.ogc.org/is/18-088/18-088.html"
    ---------------------------------------------------------------------------------------------"""

    def __init__(self):
        self.data = None

    def fetch_data(self, endpoint="Datastreams", params={}):
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
        -----------------------------------------------------------------------------------------
        """

        base_request_link = self.BASE_URL + endpoint 
        
        def single_fetch(params): #helper function for a single request
            try:
                response = requests.get(base_request_link,params)
                response.raise_for_status()
                return response.json()  # Return parsed JSON
            except requests.RequestException as e:
                print(f"ERROR <{str(e)}> occured on ENDPOINT: {endpoint} and PARAMS: {params}")
                return {"error": str(e)}

        #check if entity is accessed by ID directly, then only one datapoint
        #can be extracted and no use of ThreadPoolExecutor is necassary
        if endpoint[:-1] == ")":
            fetched_data = single_fetch(params)
            self.data = fetched_data
            return True
        
        #if $top is defined, fetch that many entries. Otherwise fetch all entries.
        entries_to_fetch = float("inf")
        if "$top" in params:
            entries_to_fetch = params["$top"]
        
        #fetching loop
        all_data = list()
        entries_fetched = 0
        while True:
            #do at most 10 requests at a time. Less if less than 10000 entries are left to fetch
            requests_to_execute = min(10,math.ceil((entries_to_fetch - entries_fetched) / 1000))

                
            params_list = list()
            for i in range(requests_to_execute):
                single_fetch_params = params
                single_fetch_params["$top"] = 1000
                single_fetch_params["$skip"] = i * 1000 + entries_fetched
                params_list.append(single_fetch_params)

            #calculate leftover entries to fetch for top param of last request.
            #Different than 1000, if non multiple of 1000 is given as entries_to_fetch
            entries_to_fetch_on_last_request = 1000
            if entries_to_fetch - entries_fetched < 10000 and entries_to_fetch % 1000 != 0:
                entries_to_fetch_on_last_request = entries_to_fetch % 1000
                params_list[-1]["$top"] == entries_to_fetch_on_last_request
            
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(single_fetch, params) for params in params_list]
                responses = [future.result() for future in futures]
                responses_json = [response.json().get("value", []) for response in responses]

                for response_json in responses_json:
                    if not response_json: #exit if response is empty, e.g. all entries have been fetched
                        break
                    all_data.extend(response_json)
            
            #update the amount of entries fetched
            entries_fetched += (requests_to_execute - 1) * 1000 + entries_to_fetch_on_last_request

            #exit if requested amount of entries have been fetched
            if entries_fetched == entries_to_fetch:
                break

            #let the API recover for a bit, testing has shown that this leads to significantly 
            #faster average response times when fetching large amounts of entries.
            time.sleep(1)
        self.data = all_data
        return True

    def get_data(self):
        if not self.data:
            raise ValueError("No data fetched yet")
        return self.data
    
    def print_raw_data(self):
        if not self.data:
            raise ValueError("No data fetched yet")
        print(json.dumps(self.data, indent=4))
    
    #------------------DEPRECATED-----------------

    def get_live_Observations_for_Datastream_id(self, id):
        # DEPRECATED
        print("DEPRECATED")
        endpoint = f"Datastreams({id})"
        params = {
            "$expand": "Observations($orderby=phenomenonTime desc;$top=1;$select=id,result,phenomenonTime)"
        }
        self.fetch_data(endpoint, params)
        print(
            f"current Status: {self.data[0]['Observations'][0]['result']}\t at Timestamp: {self.data[0]['Observations'][0]['phenomenonTime']}"
        )
        last_Observation_id = self.data[0]["Observations"][0]["@iot.id"]
        while True:
            time.sleep(1)
            self.fetch_data(endpoint, params)
            if last_Observation_id == self.data[0]["Observations"][0]["@iot.id"]:
                continue
            last_Observation_id = self.data[0]["Observations"][0]["@iot.id"]
            print(
                f"current Status: {self.data[0]['Observations'][0]['result']}\t at Timestamp: {self.data[0]['Observations'][0]['phenomenonTime']}"
            )

import requests, json


class Thing:
    BASE_URL = "https://tld.iot.hamburg.de/v1.1/Things"

    def __init__(self, idnumber: int):
        """
        Initializes a Thing instance by fetching its data from the TLD IoT Hamburg.

        Parameters:
        - idnumber (int): The @iot.id of Thing to fetch data for.
        """
        # Initial attributes
        self.id = idnumber
        self.thing_url = f"{self.BASE_URL}({self.id})"
        # Attribute obtained only if necessary
        self.data = None
        self.coordinates = None
        self.primary_signal_url = None

    def get_data(self):
        """
        Retrieves the Thing's data.

        If the data has not been fetched yet, it fetches the data from the API.

        Returns:
            dict: The data associated with the Thing.
        """
        if self.data is None:
            self._fetch_data()
        return self.data

    def get_coordinates(self):
        """
        Used to obtain geographic coordinates of Thing.

        If the coordinates have already been obtained, it returns them immediately.
        Otherwise, it fetches the Locations associated with the Thing and extracts the
        geometry information, which typically contains the coordinates as a matrix.

        Specific Raises:
            ValueError: If coordinates are not available in the response data.

        Returns:
            nested list :  containing the geographic coordinates (e.g., longitude and latitude).
        """
        if self.coordinates:
            return self.coordinates

        params = {"$expand": "Locations"}
        response = requests.get(self.thing_url, params)
        if response.status_code == 200:
            json_data = response.json()
            locations_data = json_data.get("Locations", [])
            # Check if general locations info available.
            if locations_data:
                primary_location = locations_data[0].get("location", {})
                # If available:
                # Extract geometry information (ingress lane, egress lane and real route)
                geometry = primary_location.get("geometry")
                if geometry:
                    self.coordinates = geometry["coordinates"]
                    return self.coordinates
                else:
                    raise ValueError(
                        f"No geometry information available for Thing({self.id})."
                    )
            else:
                raise ValueError(f"No Locations data available for Thing({self.id}).")
        else:
            self._handle_error(response.url)

    def last_tf_observation(self, resultTime=False):
        """
        Retrieves the latest observation for the Thing's primary signal.

        Parameters:
            return_result_time (bool): If set to True, the method returns a tuple containing
                                    (resultTime, result). Otherwise, it returns only the result.

        Returns:
            int or tuple:
                - If `return_result_time` is False, returns the latest `result` (e.g., 0).
                - If `return_result_time` is True, returns a tuple (`resultTime`, `result`).
        """
        if self.primary_signal_url is None:
            self._get_primary_signal_url()

        params = {"$expand": "Observations($top=1;$orderby=resultTime desc)"}
        response = requests.get(self.primary_signal_url, params)
        if response.status_code == 200:
            json_data = response.json()
            observations = json_data.get("Observations", [])

            if not observations:
                raise ValueError(f"No observations found for Thing({self.id}).")

            last_observation = observations[0]
            result = last_observation.get("result")

            if resultTime:
                resultTime = last_observation["resultTime"]
                return resultTime, result

            return result
        else:
            self._handle_error(response.url)

    def _fetch_data(self):
        """
        Fetches the Thing's data from the SensorThings API and updates the instance.
        """
        response = requests.get(self.thing_url)
        if response.status_code == 200:
            self.data = response.json()
        else:
            self._handle_error(response.url)

    def _handle_error(self, response_url: str):
        """
        Handles HTTP errors based on the response status code and raises a specific error
        with a descriptive message.

        Parameters:
        - response_url (str): The URL that caused an error response.
        """
        response = requests.get(response_url)
        if response.status_code == 404:
            raise requests.exceptions.HTTPError(
                f"404 Not Found Error: Thing({self.id}) could not be found!"
            )
        elif response.status_code == 400:
            raise requests.exceptions.HTTPError(
                f"400 Client Error:Bad Request for URL: {response_url}"
            )
        else:
            response.raise_for_status()

    def _get_primary_signal_url(self):
        """
        Retrieves the URL of the datastream associated with the traffic light's primary signal.
        This allows relevant information about the traffic light's current behavior to be obtained more quickly.

        The filter ensures that the correct datastream is selected online by the API.
        """
        datastreams_url = f"{self.thing_url}/Datastreams"
        params = {"$filter": "properties/layerName eq 'primary_signal'"}

        response = requests.get(datastreams_url, params)
        if response.status_code == 200:
            json_data = response.json()
            datastreams = json_data.get("value", [])

            if not datastreams:
                raise ValueError(
                    f"No primary_signal datastream found for Thing({self.id})."
                )

            # Extracting link
            self.primary_signal_url = datastreams[0].get("@iot.selfLink")

            if not self.primary_signal_url:
                raise ValueError(
                    f"@iot.selfLink is missing in the datastream for Thing({self.id})."
                )
        else:
            self._handle_error(response.url)

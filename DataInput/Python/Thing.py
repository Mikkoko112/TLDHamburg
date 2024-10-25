import requests, json


class Thing:
    BASE_URL = "https://tld.iot.hamburg.de/v1.1/Things"

    def __init__(self, idnumber: int):
        """
        Initialize a Thing instance by fetching its data from the TLD IoT Hamburg.

        Parameters:
        - idnumber (int): The @iot.id of Thing to fetch data for.
        """
        # Initial attributes
        self.id = idnumber
        self.thing_url = f"{self.BASE_URL}({self.id})"
        # Attribute obtained only if necessary
        self.primary_signal_url = None
        self.data = None
        self.coordinates = None
        self._fetch_data()

    def get_coordinates(self):
        """
        This method is used to obtain geographic coordinates of Thing.

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

    def _fetch_data(self):
        """
        This method fetches the Thing's data from the SensorThings API and updates the instance.
        """
        response = requests.get(self.thing_url)
        if response.status_code == 200:
            self.data = response.json()
        else:
            self._handle_error(response.url)

    def _handle_error(self, response_url: str):
        """
        This method handles HTTP errors based on the response status code and raises a specific error
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

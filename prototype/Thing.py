from DataFetcher import DataFetcher


class Thing:
    FETCHER = DataFetcher()

    def __init__(self, idnumber: int):
        """
        Initializes a Thing instance by fetching its data from the TLD IoT Hamburg.

        Parameters:
        - idnumber (int): The @iot.id of Thing to fetch data for.
        """
        # Initial attributes
        self.id = idnumber
        self.thing_endpoint = f"/Things({self.id})"
        # Attribute obtained only if necessary
        self.data = None
        self.coordinates = None
        self.primary_signal_endpoint = None

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

    def get_coordinates(self):  # Done
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
        # Fetching data
        params = {"$expand": "Locations"}
        self.FETCHER.fetch_data(endpoint=self.thing_endpoint, params=params)
        locations_data = self.FETCHER.data["Locations"]
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

    def get_tl_observation(self, phenomenonTime=False):
        """
        Retrieves the latest observation for the Thing's primary signal.

        Parameters:
            phenomenonTime (bool): If set to True, the method returns a tuple containing
                                    (phenomenonTime, result). Otherwise, it returns only the result.

        Returns:
            int or tuple:
                - If `phenomenonTime` is False, returns the latest `result` (e.g., 0).
                - If `phenomenonTime` is True, returns a tuple (`phenomenonTime`, `result`).
        """
        if self.primary_signal_endpoint is None:
            self._fetch_primary_signal_endpoint()

        params = {"$expand": "Observations($top=1;$orderby=phenomenonTime desc)"}
        self.FETCHER.fetch_data(self.primary_signal_endpoint, params)

        observations = self.FETCHER.data["Observations"]
        if not observations:
            raise ValueError(f"No observations found for Thing({self.id}).")

        # Extracting result of last observation
        last_observation = observations[0]
        result = last_observation["result"]

        if phenomenonTime:
            pTime = last_observation["phenomenonTime"]
            return pTime, result

        return result

    def _fetch_data(self):  # Done
        """
        Fetches the Thing's data from the SensorThings API and updates the instance.
        """
        self.FETCHER.fetch_data(endpoint=self.thing_endpoint)
        self.data = self.FETCHER.data

    def _fetch_primary_signal_endpoint(self):  # Done
        """
        Retrieves the URL of the datastream associated with the traffic light's primary signal.
        This allows relevant information about the traffic light's current behavior to be obtained more quickly.

        The filter ensures that the correct datastream is selected online by the API.
        """
        # Fetching data
        datastreams_endpoint = self.thing_endpoint + "/Datastreams"
        params = {"$filter": "properties/layerName eq 'primary_signal'"}
        self.FETCHER.fetch_data(datastreams_endpoint, params=params)
        datastreams = self.FETCHER.data

        if not datastreams:
            raise ValueError(
                f"No primary_signal datastream found for Thing({self.id})."
            )

        # Extracting endpoint
        self.primary_signal_endpoint = f'/Datastreams({datastreams[0]["@iot.id"]})'

        if self.primary_signal_endpoint is None:
            raise ValueError(
                f"@iot.id is missing in the primary signal datastream for Thing({self.id})."
            )

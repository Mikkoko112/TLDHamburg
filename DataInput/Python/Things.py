from DataFetcher import DataFetcher
from Thing import Thing
import logging


class Things:
    FETCHER = DataFetcher()
    logging.basicConfig(
        level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    def __init__(self, ids: list[int]):
        if not ids:
            raise ValueError(f"ids: list[int] is empty!")

        self.ids = ids
        self.things_endpoint = "Things"
        # Should probably not be stored, only returned as dict
        self.primary_signal_endpoint_ids = (
            dict()
        )  # Should later be stored in Thing instance
        self.coordinates = dict()  # Should later be stored in Thing instance

    def get_coordinates(self, saving=True):
        """
        Retrieves and stores the coordinates of Things based on their iot.ids.

        This method performs the following steps:
        * Checks if coordinates are already fetched and returns them if available.
        * Constructs filter query to fetch data for the specified Thing IDs.
        * Sends a request to the Things API endpoint with the filter and expansion parameters.
        * Iterates through the fetched data to extract and store geometry coordinates.
        * Logs errors for Things without location data or geometry information.

        Returns:
            dict: A dictionary mapping Thing IDs to their corresponding geometry coordinates.

        Logs:
            ERROR: If a Thing has no location data or lacks geometry information.
        """

        # Return cached coordinates if already fetched
        if self.coordinates:
            return self.coordinates

        # Build the filter query to include all Thing IDs
        filterquery = f"@iot.id eq {self.ids[0]}"
        for idn in self.ids[1:]:
            filterquery += f" or @iot.id eq {idn}"

        # API request with defined parameters, expanding Locations
        params = {"$filter": filterquery, "$expand": "Locations"}
        self.FETCHER.fetch_data(endpoint=self.things_endpoint, params=params)

        for thing_data in self.FETCHER.data:
            locations_data = thing_data["Locations"]

            if not locations_data:
                logging.error(
                    f"No Locations data available for Thing({thing_data['@iot.id']})"
                )
                continue

            # Extract the primary signal location
            primary_location = locations_data[0].get("location", {})
            geometry = primary_location.get("geometry")

            if geometry:
                self.coordinates[thing_data["@iot.id"]] = geometry["coordinates"]
            else:
                logging.error(
                    f"No geometry information available for Thing({thing_data['@iot.id']})."
                )

        # To do:
        # set the coordinates of every instance
        # Thing class needs a set_coordinates method

        return self.coordinates

    def _fetch_primary_signal_endpoint_ids(self):
        """
        Retrieves the primary signal datastream IDs and maps them to the corresponding Thing ID.

        This method performs the following steps:
        * Constructs filter query to fetch data for the specified Datastreams IDs.
        * Sends a request to the Things API endpoint with the filter and expansion parameters.
        * Iterates through the fetched data to extract the primary signal datastreams ID of the
            corresponding Thing entity.
        * Maps the primary signal datastream ID to Thing ID.
        * Logs errors for Things without datastreams or primary signal datastream.
        """

        # Construct the filter query to include all Thing ID's
        filterquery = " or ".join(f"@iot.id eq {idn}" for idn in self.ids)
        params = {"$filter": filterquery, "$expand": "Datastreams"}
        self.FETCHER.fetch_data(endpoint=self.things_endpoint, params=params)

        # Iterate through all Things
        for thing_data in self.FETCHER.data:
            datastreams = thing_data["Datastreams"]

            if not datastreams:
                logging.error(
                    f"No datastreams available for Thing({thing_data['@iot.id']})"
                )
                continue

            found_ps_endpoint = False
            # Iterate through each fetched datastreams to extract the primary signal datastream ID
            for datastream in datastreams:
                if datastream["properties"]["layerName"] == "primary_signal":
                    self.primary_signal_endpoint_ids[thing_data["@iot.id"]] = (
                        datastream["@iot.id"]
                    )
                    found_ps_endpoint = True
                    break

            if not found_ps_endpoint:
                logging.error(
                    f"No primary signal datastream available for Thing({thing_data['@iot.id']})"
                )

        # To do:
        # set the coordinates of every instance
        # Thing class needs a set_primary_signal_endpoint method

    def get_tl_observations(self, phenomenonTime=False):
        """
        Retrieves the latest observations for the primary signal datastreams associated with the specified
        Thing IDs.

        This method performs the following steps:
        * Checks if the primary signal datastream IDs have already been fetched; if not, it invokes
            `_fetch_primary_signal_endpoint_ids`.
        * Constructs a filter query to fetch observations for all primary signal datastream IDs.
        * Sends a request to the Datastreams API endpoint with the constructed filter and expansion
            parameters to retrieve the latest observations.
        * Iterates through the fetched datastreams to extract the most recent observation for each.
        * Depending on the `phenomenonTime` flag, either stores only the observation result or both the
            result and the timestamp.
        * Maps each Thing ID to its corresponding latest observation (and timestamp, if requested).
        * Logs errors for datastreams that have no observations available.
        Returns:
        dict:
            A dictionary mapping each Thing ID to its latest observation result.
            If `phenomenonTime` is `True`, each entry maps to a tuple containing
            the timestamp and the result.
        """

        if not self.primary_signal_endpoint_ids:
            self._fetch_primary_signal_endpoint_ids()

        # Construct the filter query to include all primary signal datastream IDs
        filterquery = " or ".join(
            f"@iot.id eq {d_id}" for d_id in self.primary_signal_endpoint_ids.values()
        )
        params = {
            "$filter": filterquery,
            "$expand": "Observations($top=1;$orderby=phenomenonTime desc)",
        }
        self.FETCHER.fetch_data(endpoint="Datastreams", params=params)

        # Initialize a dictionary to hold the latest observations
        tl_observations = dict()  # key: datastream id, value: tf observations

        # Iterate through each fetched datastream to extract the latest observation
        for datastream in self.FETCHER.data:
            observation = datastream["Observations"]
            if not observation:
                logging.error(
                    f"No observations found for Datastream({datastream['@iot.id']})."
                )
                continue

            last_observation = observation[0]
            result = last_observation["result"]
            if phenomenonTime:
                pTime = last_observation["phenomenonTime"]
                tl_observations[datastream["@iot.id"]] = pTime, result
            else:
                tl_observations = result

        # Map each Thing ID to its corresponding latest observation (and timestamp, if applicable)
        thing_observation = {
            key: tl_observations[value]
            for key, value in self.primary_signal_endpoint_ids.items()
            if value in tl_observations
        }

        return thing_observation

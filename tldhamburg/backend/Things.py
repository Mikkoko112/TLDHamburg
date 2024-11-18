from tldhamburg.backend.DataFetcher import DataFetcher
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
        self.primary_signal_endpoint_ids = dict()
        self.coordinates = dict()

    def _fetch_coordinates(self):
        """
        Fetches and stores the coordinates of Things based on their iot.ids.

        This method performs the following steps:
            1. Constructs filter query to fetch data for the specified Thing IDs.
            2. Sends a request to the Things API endpoint with the filter and expansion parameters.
            3. Iterates through the fetched data to extract and store geometry coordinates.
            4. Logs errors for Things without location data or geometry information.

        Logs:
            ERROR: If a Thing has no location data or lacks geometry information.
        """

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
                    f"No Locations data available for Thing({thing_data['@iot.id']})."
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

    def get_coordinates(self):
        """
        Returns the coordinates of all Things stored in the instance.

        This method performs the following steps:
            1. Fetches coordinates of all Things if not already available.
            2. Returns the coordinates.

        Returns:
            dict: A dictionary mapping Thing IDs to their corresponding geometry coordinates.

        Example:
            >>> things = Things([2])
            >>> things.get_coordinates()
            >>> print(things.coordinates)
            {
                2: [[
                        [9.9196439, 53.5638321],
                        [9.9197085, 53.5637359],
                        [9.9198219, 53.5635865],
                        [9.9198451, 53.5635559],
                        [9.9198231, 53.5634831],
                        [9.9198481, 53.563453]
                    ],
                    [
                        [9.9197087, 53.563736],
                        [9.9195566, 53.5639624],
                        [9.9195566, 53.5639624],
                        [9.919899, 53.5639529]
                    ],
                    [
                        [9.9197629, 53.5639568],
                        [9.9198989, 53.5639531],
                        [9.9200006, 53.5639497]
                    ]]
            }
        """
        if not self.coordinates:
            self._fetch_coordinates()

        return self.coordinates

    def _fetch_primary_signal_endpoint_ids(self):
        """
        Fetches the primary signal datastream IDs and maps them to the corresponding Thing ID.

        This method performs the following steps:
            1. Constructs filter query to fetch data for the specified Datastreams IDs.
            2. Sends a request to the Things API endpoint with the filter and expansion parameters.
            3. Iterates through the fetched data to extract the primary signal datastreams ID of the
                corresponding Thing entity.
            4. Maps the primary signal datastream ID to Thing ID.
            5. Logs errors for Things without datastreams or primary signal datastream.
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

    def get_primary_signal_observations(
        self, ids: list[int] = None, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for primary signal datastreams of specified Thing IDs.

        This method performs the following steps:
            1. Fetches primary signal datastream IDs if not already available.
            2. Builds a filter query for the datastream IDs.
            3. Requests the latest observations from the Datastreams API.
            4. Processes the fetched observations.
            5. Maps each Thing ID to its latest observation (and timestamp if requested).
            6. Logs errors for missing datastreams or observations.

        Args:
            ids (list[int]): Thing IDs to retrieve observations for.
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([2, 3, 18760])
            >>> obervations = things.get_tl_observations(n_obsrvtns=2, phnTime=True)
            >>> print(obervations)
            {
                2: [['2024-10-27T18:37:55Z', 1], ['2024-10-27T18:37:52Z', 2]],
                3: [['2024-10-27T18:37:55Z', 1], ['2024-10-27T18:37:52Z', 2]],
                18760: [['2024-10-27T18:37:42Z', 1], ['2024-10-27T18:37:39Z', 2]]
            }
            >>> things = Things([2, 3, 18760])
            >>> obervations = things.get_tl_observations(n_obsrvtns=1)
            >>> print(obervations)
            {
                2: [[1]],
                3: [[1]],
                18760: [[1]]
            }
        """

        if not self.primary_signal_endpoint_ids:
            self._fetch_primary_signal_endpoint_ids()

        if ids is None:
            ids = self.ids
        # Construct the filter query to include all primary signal datastream IDs
        filter_conditions = []
        for thing_id in ids:
            datastream_id = self.primary_signal_endpoint_ids.get(thing_id)
            if datastream_id:
                filter_conditions.append(f"@iot.id eq {datastream_id}")
            else:
                logging.error(
                    f"Thing({thing_id}) not found in currently observed Things."
                )

        filterquery = " or ".join(filter_conditions)

        params = {
            "$filter": filterquery,
            "$expand": f"Observations($top={n_obsrvtns};$orderby=phenomenonTime desc)",
        }
        self.FETCHER.fetch_data(endpoint="Datastreams", params=params)

        # Initialize a dictionary to hold the latest observations
        trafficlight_observations = dict()  # key: datastream id, value: tf observations

        # Iterate through each fetched datastream to extract the latest observation
        for datastream in self.FETCHER.data:
            observations = datastream["Observations"]
            if not observations:
                logging.error(
                    f"No observations found for Datastream({datastream['@iot.id']})."
                )
                continue

            # Exatracting last n observations
            thing_observations = [
                [obs["phenomenonTime"], obs["result"]] if phnTime else [obs["result"]]
                for obs in observations
            ]
            trafficlight_observations[datastream["@iot.id"]] = thing_observations

        # Map each Thing ID to its corresponding latest observation (and timestamp, if applicable)
        things_observations = {
            key: trafficlight_observations[value]
            for key, value in self.primary_signal_endpoint_ids.items()
            if value in trafficlight_observations
        }

        return things_observations

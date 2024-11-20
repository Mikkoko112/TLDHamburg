from tldhamburg.backend.DataFetcher import DataFetcher
from tldhamburg.backend.DBMaintainer import DBMaintainer
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
        self.secondary_signal_endpoint_ids = dict()
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

    def _lookup_primary_signal_endpoint_ids(self):

        self.primary_signal_endpoint_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="primary_signal"
        )

    def _lookup_secondary_signal_endpoint_ids(self):
        self.secondary_signal_endpoint_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="secondary_signal"
        )

    def _get_signal_observations(
        self,
        signal_type: str,
        ids: list[int] = None,
        n_obsrvtns: int = 1,
        phnTime: bool = False,
    ):
        """
        General method to fetch latest observations for a given signal type (primary or secondary).

        This method performs the following steps:
            1. Builds a filter query based on the datastream IDs.
            2. Requests the latest observations from the API.
            3. Processes the fetched observations.
            4. Maps each Thing ID to its latest observation (and timestamp if requested).

        Args:
            signal_type (str): The type of signal to fetch observations for. Must be either 'primary' or 'secondary'.
            ids (list[int]): Thing IDs to retrieve observations for.
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.
        """
        if signal_type == "primary":
            endpoint_ids = self.primary_signal_endpoint_ids
            lookup_method = self._lookup_primary_signal_endpoint_ids
        elif signal_type == "secondary":
            endpoint_ids = self.secondary_signal_endpoint_ids
            lookup_method = self._lookup_secondary_signal_endpoint_ids
        else:
            raise ValueError("signal_type must be either 'primary' or 'secondary'.")

        if not endpoint_ids:
            lookup_method()

        if ids is None:
            ids = self.ids

        # Construct the filter query
        filter_conditions = []
        for thing_id in ids:
            datastream_id = endpoint_ids.get(thing_id)
            # Datastream IDs zero are not
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
        # Initialize a dictionary to hold the observations
        observations_dict = {}
        # Process fetched data
        for datastream in self.FETCHER.data:
            observations = datastream.get("Observations", [])
            if not observations:
                logging.error(
                    f"No observations found for Datastream({datastream.get('@iot.id')})."
                )
                continue
            # Extract observations
            extracted_observations = [
                [obs["phenomenonTime"], obs["result"]] if phnTime else [obs["result"]]
                for obs in observations
            ]
            observations_dict[datastream["@iot.id"]] = extracted_observations
        # Map to Thing IDs
        things_observations = {
            key: observations_dict[value]
            for key, value in endpoint_ids.items()
            if value in observations_dict
        }
        return things_observations

    def get_primary_signal_observations(
        self, ids: list[int] = None, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for primary signal datastreams of specified Thing IDs.

        Args:
            ids (list[int]): Thing IDs to retrieve observations for.
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([2, 3, 18760])
            >>> obervations = things.get_primary_signal_observations(n_obsrvtns=2, phnTime=True)
            >>> print(obervations)
            {
                2: [['2024-10-27T18:37:55Z', 1], ['2024-10-27T18:37:52Z', 2]],
                3: [['2024-10-27T18:37:55Z', 1], ['2024-10-27T18:37:52Z', 2]],
                18760: [['2024-10-27T18:37:42Z', 1], ['2024-10-27T18:37:39Z', 2]]
            }
            >>> things = Things([2, 3, 18760])
            >>> obervations = things.get_primary_signal_observations(n_obsrvtns=1)
            >>> print(obervations)
            {
                2: [[1]],
                3: [[1]],
                18760: [[1]]
            }
        """
        return self._get_signal_observations(
            signal_type="primary", ids=ids, n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_secondary_signal_observations(
        self, ids: list[int] = None, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for secondary signal datastreams of specified Thing IDs.

        Args:
            ids (list[int]): Thing IDs to retrieve observations for.
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([4, 30, 6519])
            >>> observations = things.get_secondary_signal_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                4: [['2024-11-20T21:21:24Z', 0], ['2024-11-20T21:21:19Z', 3]],
                30: [['2024-11-20T21:21:24Z', 0], ['2024-11-20T21:21:19Z', 3]],
                6519: [['2024-11-20T17:55:27Z', 0], ['2024-11-20T17:55:24Z', 2]]
            }
        """
        return self._get_signal_observations(
            signal_type="secondary", ids=ids, n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

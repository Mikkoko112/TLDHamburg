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
        self.acoustic_signal_endpoints_ids = dict()
        self.detector_car_endpoints_ids = dict()
        self.detector_cyclists_endpoints_ids = dict()
        self.detector_pedestrian_endpoints_ids = dict()
        self.bus_pre_request_endpoints_ids = dict()
        self.bus_request_endpoints_ids = dict()
        self.bus_checkout_endpoints_ids = dict()
        self.signal_program_endpoints_ids = dict()
        self.cycle_second_endpoints_ids = dict()
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
        """
        Retrieves the primary signal datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.primary_signal_endpoint_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="primary_signal"
        )

    def _lookup_secondary_signal_endpoint_ids(self):
        """
        Retrieves the secondary signal datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.secondary_signal_endpoint_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="secondary_signal"
        )

    def _lookup_acoustic_signal_endpoint_ids(self):
        """
        Retrieves the acoustic signal datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.acoustic_signal_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="acoustic_signal"
        )

    def _lookup_detector_car_endpoint_ids(self):
        """
        Retrieves the car detector datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.detector_car_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="detector_car"
        )

    def _lookup_detector_cyclists_ids(self):
        """
        Retrieves the cyclists detector datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.detector_cyclists_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="detector_cyclists"
        )

    def _lookup_detector_pedestrian_ids(self):
        """
        Retrieves the pedestrian detector datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.detector_pedestrian_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="detector_pedestrian"
        )

    def _lookup_bus_pre_request_ids(self):
        """
        Retrieves the bus pre-request datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.bus_pre_request_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="bus_pre_request_point"
        )

    def _lookup_bus_request_ids(self):
        """
        Retrieves the bus request datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.bus_request_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="bus_request_point"
        )

    def _lookup_bus_checkout_ids(self):
        """
        Retrieves the bus checkout datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.bus_checkout_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="bus_checkout"
        )

    def _lookup_signal_program_endpoint_ids(self):
        """
        Retrieves the signal program datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.signal_program_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="signal_program"
        )

    def _lookup_cycle_second(self):
        """
        Retrieves the cycle second datastream IDs for the given Thing IDs from the TLDHamburg
        database and maps each Thing ID to the corresponding datastream ID.

        The result is stored in a dictionary.
        """
        self.cycle_second_endpoints_ids = DBMaintainer.read_datastreams_db(
            ids=self.ids, attribute="cycle_second"
        )

    def _get_signal_observations(
        self,
        signal_type: str,
        n_obsrvtns: int = 1,
        phnTime: bool = False,
    ):
        """
        General method to fetch latest observations for a given signal type.

        This method performs the following steps:
            1. Builds a filter query based on the datastream IDs.
            2. Requests the latest observations from the API.
            3. Processes the fetched observations.
            4. Maps each Thing ID to its latest observation (and timestamp if requested).

        Args:
            signal_type (str): The type of signal to fetch observations for.
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.
        """
        if signal_type == "primary":
            if not self.primary_signal_endpoint_ids:
                self._lookup_primary_signal_endpoint_ids()
            endpoint_ids = self.primary_signal_endpoint_ids

        elif signal_type == "secondary":
            if not self.secondary_signal_endpoint_ids:
                self._lookup_secondary_signal_endpoint_ids()
            endpoint_ids = self.secondary_signal_endpoint_ids

        elif signal_type == "acoustic":
            if not self.acoustic_signal_endpoints_ids:
                self._lookup_acoustic_signal_endpoint_ids()
            endpoint_ids = self.acoustic_signal_endpoints_ids

        elif signal_type == "detector_car":
            if not self.detector_car_endpoints_ids:
                self._lookup_detector_car_endpoint_ids()
            endpoint_ids = self.detector_car_endpoints_ids

        elif signal_type == "detector_cyclists":
            if not self.detector_cyclists_endpoints_ids:
                self._lookup_detector_cyclists_ids()
            endpoint_ids = self.detector_cyclists_endpoints_ids

        elif signal_type == "detector_pedestrian":
            if not self.detector_pedestrian_endpoints_ids:
                self._lookup_detector_pedestrian_ids()
            endpoint_ids = self.detector_pedestrian_endpoints_ids

        elif signal_type == "bus_pre_request_point":
            if not self.bus_pre_request_endpoints_ids:
                self._lookup_bus_pre_request_ids()
            endpoint_ids = self.bus_pre_request_endpoints_ids

        elif signal_type == "bus_request_point":
            if not self.bus_request_endpoints_ids:
                self._lookup_bus_request_ids()
            endpoint_ids = self.bus_request_endpoints_ids

        elif signal_type == "bus_checkout":
            if not self.bus_checkout_endpoints_ids:
                self._lookup_bus_checkout_ids()
            endpoint_ids = self.bus_checkout_endpoints_ids

        elif signal_type == "signal_program":
            if not self.signal_program_endpoints_ids:
                self._lookup_signal_program_endpoint_ids()
            endpoint_ids = self.signal_program_endpoints_ids

        elif signal_type == "cycle_second":
            if not self.cycle_second_endpoints_ids:
                self._lookup_cycle_second()
            endpoint_ids = self.cycle_second_endpoints_ids
        else:
            raise ValueError("signal type is not supported.")

        # Construct the filter query
        filter_conditions = []
        for thing_id in self.ids:
            datastream_id = endpoint_ids.get(thing_id)
            # Datastream IDs zero are not
            if datastream_id:
                filter_conditions.append(f"@iot.id eq {datastream_id}")
            else:
                logging.info(
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
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for primary signal datastreams of specified Thing IDs.

        Args:
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
            signal_type="primary", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_secondary_signal_observations(
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for secondary signal datastreams of specified Thing IDs.

        Args:
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
            signal_type="secondary", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_acoustic_signal_observations(
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for acoustic signal datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([17, 21, 3850])
            >>> observations = things.get_acoustic_signal_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                17: [['2024-11-26T08:39:19Z', 0], ['2024-11-26T08:39:05Z', 3]],
                21: [['2024-11-26T08:49:13Z', 0], ['2024-11-26T08:48:38Z', 3]],
                3850: [['2024-11-20T23:21:49Z', 0], ['2024-11-19T23:21:49Z', 0]]
            }
        """
        return self._get_signal_observations(
            signal_type="acoustic", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_detector_car_observations(self, n_obsrvtns: int = 1, phnTime: bool = False):
        """
        Fetches the latest observations for car detector datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([6, 2687, 5803])
            >>> observations = things.get_detector_car_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                6: [['2024-11-26T08:56:13Z', 0], ['2024-11-26T08:56:12Z', 40]],
                2687: [['2024-11-26T08:52:10Z', 0], ['2024-11-26T08:52:09Z', 10]],
                5803: [['2024-11-26T08:56:23Z', 100], ['2024-11-26T08:56:22Z', 60]]
            }
        """
        return self._get_signal_observations(
            signal_type="detector_car", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_detector_cyclists_observations(
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for cyclists detector datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([10, 91, 8044])
            >>> observations = things.get_detector_cyclists_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                10: [['2024-11-26T08:51:05Z', True], ['2024-11-26T08:50:51Z', False]],
                91: [['2024-11-26T08:45:20Z', False], ['2024-11-26T08:45:18Z', True]],
                8044: [['2024-11-26T08:27:46Z', False], ['2024-11-26T08:27:45Z', True]]
            }
        """
        return self._get_signal_observations(
            signal_type="detector_cyclists", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_detector_pedestrian_observations(
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for pedestrian detector datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([1310, 2826, 23514])
            >>> observations = things.get_detector_pedestrian_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                1310: [['2024-11-30T12:25:55Z', False], ['2024-11-30T12:25:53Z', True]],
                2826: [['2024-11-29T23:21:49Z', False], ['2024-11-25T23:21:45Z', False]],
                23514: [['2024-11-30T12:40:22Z', False], ['2024-11-30T12:40:21Z', True]]
            }
        """
        return self._get_signal_observations(
            signal_type="detector_pedestrian", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_bus_pre_request_point_observations(
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for bus pre request point datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([27,28,29])
            >>> observations = things.get_bus_pre_request_point_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                27: [['2024-11-30T12:41:49Z', 3], ['2024-11-30T12:38:56Z', 3]],
                28: [['2024-11-30T12:41:49Z', 3], ['2024-11-30T12:38:56Z', 3]],
                29: [['2024-11-28T21:43:12Z', 288], ['2024-11-28T20:43:03Z', 288]]
            }
        """
        return self._get_signal_observations(
            signal_type="bus_pre_request_point", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_bus_request_point_observations(
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for bus request point datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([27, 28, 29])
            >>> observations = things.get_bus_request_point_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                27: [['2024-11-30T12:53:25Z', 3], ['2024-11-30T12:52:26Z', 3]],
                28: [['2024-11-30T12:53:25Z', 3], ['2024-11-30T12:52:26Z', 3]],
                29: [['2024-11-30T12:54:24Z', 2], ['2024-11-30T12:54:24Z', 2]]
            }
        """
        return self._get_signal_observations(
            signal_type="bus_request_point", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_bus_checkout_observations(self, n_obsrvtns: int = 1, phnTime: bool = False):
        """
        Fetches the latest observations for bus checkout datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([27, 28, 31])
            >>> observations = things.get_bus_checkout_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                27: [['2024-11-30T12:59:56Z', 3], ['2024-11-30T12:53:42Z', 3]],
                28: [['2024-11-30T12:59:56Z', 3], ['2024-11-30T12:53:42Z', 3]],
                30: [['2024-11-30T12:54:29Z', 2], ['2024-11-30T12:42:25Z', 2]]
            }
        """
        return self._get_signal_observations(
            signal_type="bus_checkout", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_signal_program_observations(
        self, n_obsrvtns: int = 1, phnTime: bool = False
    ):
        """
        Fetches the latest observations for signal program datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([2, 3, 6])
            >>> observations = things.get_signal_program_observations(n_obsrvtns=2, phnTime=True)
            >>> print(observations)
            {
                2: [['2024-11-26T04:01:50Z', 1], ['2024-11-25T23:01:30Z', 2]],
                3: [['2024-11-26T04:01:50Z', 1], ['2024-11-25T23:01:30Z', 2]],
                6: [['2024-11-26T04:01:50Z', 1], ['2024-11-25T23:01:30Z', 2]]
            }
        """
        return self._get_signal_observations(
            signal_type="signal_program", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

    def get_cycle_second_observations(self, n_obsrvtns: int = 1, phnTime: bool = False):
        """
        Fetches the latest observations for cycle second datastreams of specified Thing IDs.

        Args:
            n_obsrvtns (int, optional): Number of recent observations per datastream. Defaults to 1.
            phnTime (bool, optional): Include phenomenon time with each observation. Defaults to False.

        Returns:
            dict: Maps each Thing ID to its latest observation result.
                If `phnTime` is True, maps to a list of (timestamp, result) tuples.

        Examples:
            >>> things = Things([2, 3, 5])
            >>> observations = things.get_cycle_second_observations(n_obsrvtns=3, phnTime=True)
            >>> print(observations)
            {
                2: [['2024-11-30T22:59:59Z', 0], ['2024-11-30T13:01:30Z', 0], ['2024-11-30T13:00:00Z', 0]],
                3: [['2024-11-30T22:59:59Z', 0], ['2024-11-30T13:01:30Z', 0], ['2024-11-30T13:00:00Z', 0]],
                5: [['2024-11-30T22:59:59Z', 0], ['2024-11-30T13:01:30Z', 0], ['2024-11-30T13:00:00Z', 0]]
            }
        """
        return self._get_signal_observations(
            signal_type="cycle_second", n_obsrvtns=n_obsrvtns, phnTime=phnTime
        )

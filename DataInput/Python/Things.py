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
        self.last_observations = dict()
        self.coordinates = dict()

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

        # API request with defined parameters
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
                print(geometry["coordinates"])
            else:
                logging.error(
                    f"No geometry information available for Thing({thing_data['@iot.id']})."
                )

        return self.coordinates

    def _fetch_primary_signal_endpoints(self):
        pass

    def get_tf_observations(self, ids: list[int]):
        pass

    def get_latest_tf_observations(self, ids: list[int]):
        pass

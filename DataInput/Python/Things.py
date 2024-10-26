class Things:
    BASE_URL = "https://tld.iot.hamburg.de/v1.1/Things"

    def __init__(self, ids: list[int]):
        self.ids = ids
        self.last_observations = list()
        self.data = dict()

    def get_data(self):
        pass

    def get_coordinates(self):
        pass

    def _fetch_data(self):
        pass

    def _handle_error(self):
        pass

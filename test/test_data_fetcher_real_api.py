import unittest
from unittest.mock import patch, MagicMock
from tldhamburg.backend.DataFetcher import DataFetcher

class TestFetchData(unittest.TestCase):
    """Integration tests for DataFetcher.fetch_data()

    Test if API is available.
    """

    def test_API_availability(self):
        endpoint = "Things"
        params = {"$top": 1}
        data_fetcher = DataFetcher()

        try:
            data_fetcher.fetch_data(endpoint, params)
            data = data_fetcher.get_data()

            # Assert that data is not None and contains expected structure
            self.assertIsNotNone(data, "API returned no data.")
            self.assertTrue(len(data) > 0, "API returned an empty dataset.")

        except Exception as e:
            self.fail(f"API call failed with exception: {e}")
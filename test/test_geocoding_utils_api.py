import unittest
from unittest.mock import patch, MagicMock
from tldhamburg.frontend.geocoding_utils import return_coordinates

class TestGeocodingUtils(unittest.TestCase):
    """Integration tests for gecoding_utils.return_coordinates

    Test if API is available.
    """

    def test_API_availability(self):
        address = "Hauptbahnhof"
        
        try:
            coordinates = return_coordinates(address)

            # Assert that data is not None
            self.assertIsNotNone(coordinates, "API returned no data.")

        except Exception as e:
            self.fail(f"API call failed with exception: {e}")
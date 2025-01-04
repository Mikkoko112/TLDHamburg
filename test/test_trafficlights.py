import unittest
from unittest.mock import MagicMock, patch
from tldhamburg.frontend.trafficlights import Trafficlight

class TestTrafficlight(unittest.TestCase):
    def setUp(self):
        # Initialize
        self.tl = Trafficlight(things_id=18670, 
                          lat=9.98986339569092, 
                          lon=53.5612106323242, 
                          object_type="primary_signal")

    def test_get_coordinates_latlon(self):
        # Setup 
        result1 = tuple(self.tl.get_coordinates(option="latlon"))
        result2 = tuple(self.tl.get_coordinates(option="lonlat"))

        # Expected result
        expected_result1 = (self.tl._lat, self.tl._lon)
        expected_result2 = (self.tl._lon, self.tl._lat)

        # Assert
        self.assertEqual(result1, expected_result1)
        self.assertEqual(result2, expected_result2)

    def test_set_get_status(self):
        # Setup
        self.tl.set_status(status="red")
        result = self.tl.get_status()

        # Expected result
        expected_result = "red"

        # Assert
        self.assertEqual(result, expected_result)


            

if __name__ == "__main__":
    unittest.main()

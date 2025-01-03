import unittest
from unittest.mock import MagicMock, patch
from tldhamburg.frontend.trafficlights import Trafficlight

class TestTrafficlight(unittest.TestCase):
    def test_position(self):
        # Setup
        tl = Trafficlight(things_id=18670, 
                          lat=9.98986339569092, 
                          lon=53.5612106323242, 
                          object_type="primary_signal")

        def test_get_coordinates_latlon(self):
            # Setup 
            result1 = tuple(tl.get_coordinates(self, option="latlon"))
            result2 = tuple(tl.get_coordinates(self,option="lonlat"))

            # Expected result
            expected_result1 = (tl._lat, tl._lon)
            expected_result2 = (tl._lon, tl._lat)

            # Assert
            self.assertEqual(result1, expected_result1)
            self.assertEqual(result2, expected_result2)

        def test_set_get_status(self):
            # Setup
            tl.set_status(status="red")
            result = tl.get_status()

            # Expected result
            expected_result = "red"

            # Assert
            self.assertEqual(result, expected_result)


            

if __name__ == "__main__":
    unittest.main()

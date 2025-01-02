import unittest
from unittest.mock import MagicMock, patch
from tldhamburg.frontend.get_objects import get_marker
from tldhamburg.frontend.get_objects import get_trafficlights
import dash_leaflet as dl

class TestGetMarker(unittest.TestCase):
    """Unit test for get_objects.get_marker
    """
    def test_get_marker(self):
        # Setup
        dep_dest = [{"id": "start", "lat": 53.5975929, "lon": 9.9318831},
               {"id": "end", "lat": 53.5524079, "lon": 10.0084222}]      
        
        # Call the method under test
        result = get_marker(dep_dest)

        # Expected result
        expected_result = [
            dl.Marker(position=[53.5975929, 9.9318831],
                children=[
                    dl.Tooltip("start"),
                ]),
            dl.Marker(position=[53.5524079, 10.0084222],
                children=[
                    dl.Tooltip("end"),
                ])
        ]

        # Assert
        self.assertEqual(result, expected_result)

    #def test_get_trafficlights(lights):
        # Setup

if __name__ == "__main__":
    unittest.main()
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
        dep_dest = [{"id": "departure", "lat": 53.5975929, "lon": 9.9318831},
               {"id": "destination", "lat": 53.5524079, "lon": 10.0084222}]      
        
        # Call the method under test
        result = get_marker(dep_dest)

        # Expected result
        expected_result = [
                    dl.Marker(children=[dl.Tooltip('departure')], position=[53.5975929, 9.9318831]),
                    dl.Marker(children=[dl.Tooltip('destination')], position=[53.5524079, 10.0084222])
                ]

        # Assert
        #self.assertEqual(result, expected_result)
        for r, e in zip(result, expected_result):
            self.assertEqual(len(r.children), len(e.children))  # Compare children lengths
            self.assertEqual(r.position, e.position)
            self.assertEqual(r.children[0].children, e.children[0].children)  # Compare Tooltip text

    #def test_get_trafficlights(lights):
        # Setup

if __name__ == "__main__":
    unittest.main()
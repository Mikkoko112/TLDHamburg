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
                    dl.CircleMarker(children=[dl.Tooltip('departure')], center=[53.5975929, 9.9318831], color='blue', radius=10),
                    dl.CircleMarker(children=[dl.Tooltip('destination')], center=[53.5524079, 10.0084222], color='black', radius=10)
                ]

        # Assert
        #self.assertEqual(result, expected_result)
        for r, e in zip(result, expected_result):
            self.assertEqual(len(r.children), len(e.children))  # Compare children lengths
            self.assertEqual(r.center, e.center)
            self.assertEqual(r.children[0].children, e.children[0].children)  # Compare Tooltip text
            self.assertEqual(r.color, e.color)
            self.assertEqual(r.radius, e.radius)

    def test_get_trafficlights(self):
        # Setup
        lights = [[9.90627193450928, 53.5681304931641], [9.90691184997559, 53.5672760009766]]
        
        # Call the method under test
        result = get_trafficlights(lights)

        # Expected result
        expected_result = [
            dl.Marker(children=[dl.Tooltip('Traffic Light')], position=[53.5681304931641, 9.90627193450928]), 
            dl.Marker(children=[dl.Tooltip('Traffic Light')], position=[53.5672760009766, 9.90691184997559])]
        
        for r,e in zip(result, expected_result):
            self.assertEqual(len(r.children), len(e.children))  # Compare children lengths
            self.assertEqual(r.position, e.position)
            self.assertEqual(r.children[0].children, e.children[0].children)  # Compare Tooltip text


if __name__ == "__main__":
    unittest.main()
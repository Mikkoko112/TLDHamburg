import unittest
from unittest.mock import patch, MagicMock
from tldhamburg.frontend.geocoding_utils import return_coordinates
from tldhamburg.frontend.geocoding_utils import convert_to_lat_lon


class TestReturnCoordinates(unittest.TestCase):
    """Unit test for gecoding_utils.return_coordinates
    """

    def test_return_coordinates(self):
        # Setup
        address = "Hauptbahnhof"

        # Create a mock geolocator
        mock_geolocator = MagicMock()

        # Create a mock geocode return value
        mock_geocode_info = MagicMock()
        mock_geocode_info.raw = {'place_id': 132238811, 
                                'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright', 
                                'osm_type': 'node', 
                                'osm_id': 3501182065, 
                                'lat': '53.5524079', 
                                'lon': '10.0084222', 
                                'class': 'railway', 
                                'type': 'subway_entrance', 
                                'place_rank': 30, 
                                'importance': 8.255359731436664e-05, 
                                'addresstype': 'railway', 
                                'name': 'Hauptbahnhof', 
                                'display_name': 'Hauptbahnhof, Kirchenallee, St. Georg, Hamburg-Mitte, Hamburg, 20099, Deutschland', 
                                'boundingbox': ['53.5523579', '53.5524579', '10.0083722', '10.0084722']}
        mock_geocode_info.latitude = 53.5524079
        mock_geocode_info.longitude = 10.0084222

        # Set the return value of geocode method
        mock_geolocator.geocode.return_value = mock_geocode_info

        coordinates = return_coordinates(address, mock_geolocator)

        # Expected result
        expected_result = (53.5524079, 10.0084222)
        
        # Assert
        self.assertEqual(coordinates, expected_result)

class TestConvertToLatLon(unittest.TestCase):
    """Unit test for gecoding_utils.convert_to_lat_lon
    """

    def test_convert_to_lat_lon(self):
        # Setup
        lonlat = [10.0084222,53.5524079]

        coordinates = convert_to_lat_lon(lonlat)

        # Expected result
        expected_result = [53.5524079, 10.0084222]

        # Assert
        self.assertEqual(coordinates, expected_result)
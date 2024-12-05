import unittest
from unittest.mock import patch, MagicMock
from tldhamburg.backend.DataFetcher import DataFetcher

class TestFetchData(unittest.TestCase):
    """     Unit tests for DataFetcher.fetch_data()
    
    API responses get replaced by mock responses to test if error handling
    and data handling is implemented as intended"""

    @patch('requests.get')
    def test_single_fetch(self, mock_get):
        # Mock a single API response
        mock_response = {
            "value": [
                {"@iot.id": 1, "name": "Thing 1"},
                {"@iot.id": 2, "name": "Thing 2"}
            ]
        }
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response)

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="Things", params={"$top": 2})

        self.assertEqual(len(fetcher.get_data()), 2)
        self.assertEqual(fetcher.get_data()[0]['name'], "Thing 1")

    @patch('requests.get')
    def test_invalid_endpoint(self, mock_get):
        # Simulate a 404 Not Found response
        mock_get.return_value = MagicMock(status_code=404)

        fetcher = DataFetcher()
        with self.assertRaises(ValueError):
            fetcher.fetch_data(endpoint="InvalidEndpoint")

    @patch('requests.get')
    def test_pagination(self, mock_get):
        # Mock paginated responses
        first_page = {
            "value": [
                {"@iot.id": 1, "name": "Thing 1"}
            ],
            "@iot.nextLink": "https://tld.iot.hamburg.de/v1.1/Things?$top=1&$skip=1"
        }
        second_page = {
            "value": [
                {"@iot.id": 2, "name": "Thing 2"}
            ]
        }

        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: first_page),
            MagicMock(status_code=200, json=lambda: second_page)
        ]

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="Things", params={"$top": 1001})
        
        self.assertEqual(len(fetcher.get_data()), 2)
        self.assertEqual(fetcher.get_data()[1]['name'], "Thing 2")

    @patch('requests.get')
    def test_invalid_params(self, mock_get):
        # Simulate a 400 Bad Request response
        mock_response = {
            "code": 400,
            "message": "Invalid parameter"
        }
        mock_get.return_value = MagicMock(status_code=400, json=lambda: mock_response)

        fetcher = DataFetcher()
        with self.assertRaises(ValueError):
            fetcher.fetch_data(endpoint="Things", params={"$invalid": 1})

class TestGetData(unittest.TestCase):
    def test_get_no_data(self):
        fetcher = DataFetcher()
        with self.assertRaises(ValueError):
            fetcher.get_data()

    @patch('requests.get')
    def test_get_data_fetched(self, mock_get):
        mock_response = {
            "value": [
                {"@iot.id": 1, "name": "Thing 1"}
            ]
        }
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response)

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="Things", params={"$top": 1})

        self.assertEqual(len(fetcher.get_data()), 1)
        self.assertEqual(fetcher.get_data()[0]['name'], "Thing 1")

class TestPrintData(unittest.TestCase):
    @patch('requests.get')
    def test_print(self, mock_get):
        mock_response = {
            "value": [
                {"@iot.id": 1, "name": "Thing 1"}
            ]
        }
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response)

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="Things", params={"$top": 1})

        with patch('builtins.print') as mock_print:
            fetcher.print_raw_data()
            mock_print.assert_called()

if __name__ == "__main__":
    unittest.main()

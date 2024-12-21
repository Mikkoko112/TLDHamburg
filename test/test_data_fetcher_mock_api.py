import unittest
import requests
import logging
from unittest.mock import patch, MagicMock
from tldhamburg.backend.DataFetcher import DataFetcher

class TestGetErrors(unittest.TestCase):
    """     Unit tests for DataFetcher.get_errors()      """

    @classmethod
    def setUpClass(self):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(self):
        logging.disable(logging.NOTSET)
    
    def test_no_errors_occured(self):
        fetcher = DataFetcher()
        self.assertIsNone(fetcher.get_errors())

    def test_get_occured_errors(self):
        fetcher = DataFetcher()
        fetcher.errors = ["TestError"]

        self.assertEqual(len(fetcher.get_errors()), 1)
        self.assertEqual(fetcher.get_errors()[0], "TestError")

class TestGetData(unittest.TestCase):
    """     Unit tests for DataFetcher.get_data()      """

    @classmethod
    def setUpClass(self):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(self):
        logging.disable(logging.NOTSET)
    
    def test_no_data_fetched(self):
        fetcher = DataFetcher()
        self.assertIsNone(fetcher.get_data())

    def test_get_data_fetched(self):
        fetcher = DataFetcher()
        fetcher.data = ["TestData"]

        self.assertEqual(len(fetcher.get_data()), 1)
        self.assertEqual(fetcher.get_data()[0], "TestData")

class TestPrintData(unittest.TestCase):
    """     Unit tests for DataFetcher.print_data()      """

    @classmethod
    def setUpClass(self):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(self):
        logging.disable(logging.NOTSET)
    
    @patch('builtins.print')
    def test_print(self, mock_print):
        fetcher = DataFetcher()
        fetcher.print_raw_data()
        self.assertEqual(mock_print.call_count, 1)

class TestFetchData(unittest.TestCase):
    """     Unit tests for DataFetcher.fetch_data()
    
    API responses get replaced by mock responses to test if error handling
    and data handling is implemented as intended      """

    @classmethod
    def setUpClass(self):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(self):
        logging.disable(logging.NOTSET)

    @patch('requests.get')
    def test_single_fetch(self, mock_get):
        #Mock a single API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {"@iot.id": 1, "name": "Thing 1"},
            ]
        }
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="Things", params={"$top": 1})

        self.assertEqual(mock_get.call_count,1)
        self.assertEqual(len(fetcher.get_data()), 1)
        self.assertIsNone(fetcher.get_errors())
        self.assertEqual(fetcher.get_data()[0]['name'], "Thing 1")

    @patch('requests.get')
    def test_direct_fetch(self, mock_get):
        #Mock a single API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"@iot.id": 1, "name": "Thing 1"}
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="Things(23229)", params={})
        

        self.assertEqual(mock_get.call_count,1)
        self.assertEqual(len(fetcher.get_data()), 1)
        self.assertIsNone(fetcher.get_errors())
        self.assertEqual(fetcher.get_data()[0]['name'], "Thing 1")

    @patch('requests.get')
    def test_large_fetch(self, mock_get):
        #Mock a large fetch with >1000 entries to fetch

        def create_mock_response(i):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "value": [
                    {"@iot.id": i, "name": f"Thing {i}"},
                ]
            }
            return mock_response
        
        mock_get.side_effect = [create_mock_response(i) for i in range(1,4)]

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="Things", params={"$top": 2500})
        
        self.assertEqual(mock_get.call_count,3)
        self.assertEqual(len(fetcher.get_data()), 3)
        self.assertIsNone(fetcher.get_errors())
        self.assertEqual(fetcher.get_data()[0]['name'], "Thing 1")
        self.assertEqual(fetcher.get_data()[1]['name'], "Thing 2")
        self.assertEqual(fetcher.get_data()[2]['name'], "Thing 3")

    @patch('requests.get')
    def test_invalid_endpoint(self, mock_get):
        #Simulate a 404 Not Found response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error: Not Found")
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="InvalidEndpoint",params={"$top": 1})
        
        self.assertEqual(mock_get.call_count,1)
        self.assertIsNone(fetcher.get_data())
        self.assertEqual(len(fetcher.get_errors()),1)
        self.assertEqual(fetcher.get_errors()[0], '404 Client Error: Not Found')

    @patch('requests.get')
    def test_invalid_params(self, mock_get):
        #Simulate a 404 Not Found response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Query is not valid")
        mock_get.return_value = mock_response

        fetcher = DataFetcher()
        fetcher.fetch_data(endpoint="InvalidEndpoint",params={"$top": 1})
        
        self.assertEqual(mock_get.call_count,1)
        self.assertIsNone(fetcher.get_data())
        self.assertEqual(len(fetcher.get_errors()),1)
        self.assertEqual(fetcher.get_errors()[0], '400 Query is not valid')

if __name__ == "__main__":
    unittest.main()
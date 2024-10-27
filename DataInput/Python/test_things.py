import unittest
from unittest.mock import MagicMock, patch
from Things import Things  # Assuming the Things class is in Things.py


class TestGetCoordinates(unittest.TestCase):
    def test_get_coordinates(self):
        # Setup
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 2,
                    "Locations": [
                        {
                            "location": {
                                "geometry": {
                                    "coordinates": [
                                        [[9.9196439, 53.5638321]],
                                        [[9.9197087, 53.563736]],
                                        [[9.9197629, 53.5639568]],
                                    ]
                                }
                            }
                        }
                    ],
                },
                {
                    "@iot.id": 3,
                    "Locations": [
                        {
                            "location": {
                                "geometry": {
                                    "coordinates": [
                                        [[9.9196439, 53.5638321]],
                                        [[9.9197087, 53.563736]],
                                        [[9.9197646, 53.5639853]],
                                    ]
                                }
                            }
                        }
                    ],
                },
                {
                    "@iot.id": 18760,
                    "Locations": [
                        {
                            "location": {
                                "geometry": {
                                    "coordinates": [
                                        [[9.9860901, 53.5477193]],
                                        [[9.9860228, 53.5477378]],
                                        [[9.9869255, 53.5475913]],
                                    ]
                                }
                            }
                        }
                    ],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        result = things.get_coordinates()

        # Expected result
        excepted_result = {
            2: [
                [[9.9196439, 53.5638321]],
                [[9.9197087, 53.563736]],
                [[9.9197629, 53.5639568]],
            ],
            3: [
                [[9.9196439, 53.5638321]],
                [[9.9197087, 53.563736]],
                [[9.9197646, 53.5639853]],
            ],
            18760: [
                [[9.9860901, 53.5477193]],
                [[9.9860228, 53.5477378]],
                [[9.9869255, 53.5475913]],
            ],
        }

        # Assert
        self.assertEqual(result, excepted_result)

    def test_get_coordinates_no_location_data(self):
        # Setup
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 2,
                    "Locations": [],
                },
                {
                    "@iot.id": 3,
                    "Locations": [],
                },
                {
                    "@iot.id": 18760,
                    "Locations": [],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        result = things.get_coordinates()
        # Not ready
        pass

    def test_get_coordinates_no_geometry(self):
        # Setup
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 2,
                    "Locations": [{"location": {"geometry": {}}}],
                },
                {
                    "@iot.id": 3,
                    "Locations": [{"location": {"geometry": {}}}],
                },
                {
                    "@iot.id": 18760,
                    "Locations": [{"location": {"geometry": {}}}],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        result = things.get_coordinates()
        # Not ready
        pass


class TestFetchPrimarySignalEndpointIds(unittest.TestCase):
    # To be done!
    pass


class TestGetTLObservations(unittest.TestCase):
    def test_get_tl_observations_valid_ids_phnTime_false(self):
        # Setup
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        # Mock data for _fetch_primary_signal_endpoint_ids()
        def side_effect_fetch_data(endpoint, params):
            if endpoint == "Things":
                # This is for _fetch_primary_signal_endpoint_ids()
                # Set the data to simulate what would be returned from the API
                mock_fetcher.data = [
                    {
                        "@iot.id": 2,
                        "Datastreams": [
                            {
                                "@iot.id": 1002,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    {
                        "@iot.id": 3,
                        "Datastreams": [
                            {
                                "@iot.id": 1003,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    {
                        "@iot.id": 18760,
                        "Datastreams": [
                            {
                                "@iot.id": 2000,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                ]
            elif endpoint == "Datastreams":
                # This is for get_tl_observations()
                # Set the data to simulate observations
                mock_fetcher.data = [
                    {
                        "@iot.id": 1002,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 1}
                        ],
                    },
                    {
                        "@iot.id": 1003,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 2}
                        ],
                    },
                    {
                        "@iot.id": 2000,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:42Z", "result": 3}
                        ],
                    },
                ]
            else:
                mock_fetcher.data = []

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        result = things.get_tl_observations(ids, n_obsrvtns=1, phnTime=False)

        # Expected result
        expected_result = {
            2: [[1]],
            3: [[2]],
            18760: [[3]],
        }

        # Assert
        self.assertEqual(result, expected_result)

    def test_get_tl_observations_valid_ids_phnTime_true_n_obsrvtns_2(self):
        # Setup
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        # Mock data for _fetch_primary_signal_endpoint_ids()
        def side_effect_fetch_data(endpoint, params):
            if endpoint == "Things":
                mock_fetcher.data = [
                    {
                        "@iot.id": 2,
                        "Datastreams": [
                            {
                                "@iot.id": 1002,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    {
                        "@iot.id": 3,
                        "Datastreams": [
                            {
                                "@iot.id": 1003,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    {
                        "@iot.id": 18760,
                        "Datastreams": [
                            {
                                "@iot.id": 2000,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                ]
            elif endpoint == "Datastreams":
                mock_fetcher.data = [
                    {
                        "@iot.id": 1002,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 1},
                            {"phenomenonTime": "2024-10-27T18:37:52Z", "result": 2},
                        ],
                    },
                    {
                        "@iot.id": 1003,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 3},
                            {"phenomenonTime": "2024-10-27T18:37:52Z", "result": 4},
                        ],
                    },
                    {
                        "@iot.id": 2000,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:42Z", "result": 5},
                            {"phenomenonTime": "2024-10-27T18:37:39Z", "result": 6},
                        ],
                    },
                ]
            else:
                mock_fetcher.data = []

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        result = things.get_tl_observations(ids, n_obsrvtns=2, phnTime=True)

        # Expected result
        expected_result = {
            2: [["2024-10-27T18:37:55Z", 1], ["2024-10-27T18:37:52Z", 2]],
            3: [["2024-10-27T18:37:55Z", 3], ["2024-10-27T18:37:52Z", 4]],
            18760: [["2024-10-27T18:37:42Z", 5], ["2024-10-27T18:37:39Z", 6]],
        }

        # Assert
        self.assertEqual(result, expected_result)

    def test_get_tl_observations_with_missing_ids(self):
        # Setup
        ids = [2, 3, 18760, 999]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            if endpoint == "Things":
                mock_fetcher.data = [
                    {
                        "@iot.id": 2,
                        "Datastreams": [
                            {
                                "@iot.id": 1002,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    {
                        "@iot.id": 3,
                        "Datastreams": [
                            {
                                "@iot.id": 1003,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    # Note: 18760 and 999 are missing
                ]
            elif endpoint == "Datastreams":
                mock_fetcher.data = [
                    {
                        "@iot.id": 1002,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 1}
                        ],
                    },
                    {
                        "@iot.id": 1003,
                        "Observations": [
                            {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 2}
                        ],
                    },
                ]
            else:
                mock_fetcher.data = []

        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        with patch("logging.error") as mock_logging_error:
            result = things.get_tl_observations(ids, n_obsrvtns=1, phnTime=False)

            expected_result = {
                2: [[1]],
                3: [[2]],
            }

            self.assertEqual(result, expected_result)

            # Check that logging.error was called for the missing IDs
            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("Thing(18760) not found in currently observed Things.", calls)
            self.assertIn("Thing(999) not found in currently observed Things.", calls)

    def test_get_tl_observations_no_observations(self):
        # Setup
        ids = [2, 3, 18760]
        things = Things(ids)

        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            if endpoint == "Things":
                mock_fetcher.data = [
                    {
                        "@iot.id": 2,
                        "Datastreams": [
                            {
                                "@iot.id": 1002,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    {
                        "@iot.id": 3,
                        "Datastreams": [
                            {
                                "@iot.id": 1003,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                    {
                        "@iot.id": 18760,
                        "Datastreams": [
                            {
                                "@iot.id": 2000,
                                "properties": {"layerName": "primary_signal"},
                            },
                        ],
                    },
                ]
            elif endpoint == "Datastreams":
                mock_fetcher.data = [
                    {"@iot.id": 1002, "Observations": []},
                    {"@iot.id": 1003, "Observations": []},
                    {"@iot.id": 2000, "Observations": []},
                ]
            else:
                mock_fetcher.data = []

        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        with patch("logging.error") as mock_logging_error:
            result = things.get_tl_observations(ids, n_obsrvtns=1, phnTime=False)

            expected_result = {}
            self.assertEqual(result, expected_result)

            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("No observations found for Datastream(1002).", calls)
            self.assertIn("No observations found for Datastream(1003).", calls)
            self.assertIn("No observations found for Datastream(2000).", calls)

    def test_get_tl_observations_empty_ids(self):
        # Setup
        ids = []
        things = Things([1, 2, 3])  # Must instantiate with non-empty ids

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        # Assume primary_signal_endpoint_ids is already fetched
        things.primary_signal_endpoint_ids = {
            1: 1001,
            2: 1002,
            3: 1003,
        }

        result = things.get_tl_observations(ids, n_obsrvtns=1, phnTime=False)

        expected_result = {}
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
from tldhamburg.backend.Things import Things


class TestFetchCoordinates(unittest.TestCase):
    def test_fetch_coordinates(self):
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
        things._fetch_coordinates()
        result = things.coordinates

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

    def test_fetch_coordinates_no_location_data(self):
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
        with patch("logging.error") as mock_logging_error:
            things._fetch_coordinates()
            result = things.coordinates

            expected_result = {}
            self.assertEqual(result, expected_result)

            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("No Locations data available for Thing(2).", calls)
            self.assertIn("No Locations data available for Thing(3).", calls)
            self.assertIn("No Locations data available for Thing(18760).", calls)

    def test_fetch_coordinates_no_geometry(self):
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
        with patch("logging.error") as mock_logging_error:
            things._fetch_coordinates()
            result = things.coordinates

            expected_result = {}
            self.assertEqual(result, expected_result)

            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("No geometry information available for Thing(2).", calls)
            self.assertIn("No geometry information available for Thing(3).", calls)
            self.assertIn("No geometry information available for Thing(18760).", calls)


class TestFetchPrimarySignalEndpointIds(unittest.TestCase):
    def test_fetch_primary_signal_endpoint_ids(self):
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 2,
                    "Datastreams": [
                        {
                            "@iot.id": 15,
                            "properties": {"layerName": "primary_signal"},
                        },
                        {
                            "@iot.id": 13,
                            "properties": {"layerName": "detector_car"},
                        },
                    ],
                },
                {
                    "@iot.id": 3,
                    "Datastreams": [
                        {
                            "@iot.id": 6,
                            "properties": {"layerName": "primary_signal"},
                        },
                        {
                            "@iot.id": 36,
                            "properties": {"layerName": "detector_car"},
                        },
                    ],
                },
                {
                    "@iot.id": 18760,
                    "Datastreams": [
                        {
                            "@iot.id": 70477,
                            "properties": {"layerName": "primary_signal"},
                        },
                        {
                            "@iot.id": 74652,
                            "properties": {"layerName": "detector_car"},
                        },
                    ],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        things._fetch_primary_signal_endpoint_ids()
        result = things.primary_signal_endpoint_ids

        # Expected result
        expected_result = {2: 15, 3: 6, 18760: 70477}

        # Assert
        self.assertEqual(result, expected_result)

    def test_fetch_primary_signal_endpoint_ids_no_datastream(self):
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 2,
                    "Datastreams": [],
                },
                {
                    "@iot.id": 3,
                    "Datastreams": [],
                },
                {
                    "@iot.id": 18760,
                    "Datastreams": [],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        with patch("logging.error") as mock_logging_error:
            things._fetch_primary_signal_endpoint_ids()
            result = things.primary_signal_endpoint_ids

            expected_result = {}
            self.assertEqual(result, expected_result)

            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("No datastreams available for Thing(2)", calls)
            self.assertIn("No datastreams available for Thing(3)", calls)
            self.assertIn("No datastreams available for Thing(18760)", calls)

    def test_fetch_primary_signal_endpoint_ids_no_primary_signal_datastream(self):
        ids = [2, 3, 18760]
        things = Things(ids)

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 2,
                    "Datastreams": [
                        {
                            "@iot.id": 13,
                            "properties": {"layerName": "detector_car"},
                        },
                    ],
                },
                {
                    "@iot.id": 3,
                    "Datastreams": [
                        {
                            "@iot.id": 36,
                            "properties": {"layerName": "detector_car"},
                        },
                    ],
                },
                {
                    "@iot.id": 18760,
                    "Datastreams": [
                        {
                            "@iot.id": 74652,
                            "properties": {"layerName": "detector_car"},
                        },
                    ],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        with patch("logging.error") as mock_logging_error:
            things._fetch_primary_signal_endpoint_ids()
            result = things.primary_signal_endpoint_ids

            expected_result = {}
            self.assertEqual(result, expected_result)

            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("No primary signal datastream available for Thing(2)", calls)
            self.assertIn("No primary signal datastream available for Thing(3)", calls)
            self.assertIn(
                "No primary signal datastream available for Thing(18760)", calls
            )


class TestLookUpPrimarySignalEndpointIds(unittest.TestCase):
    def test_lookup_primary_signal_endpoint_ids_non_zero(self):
        ids = [2, 3, 4, 8, 10, 18760]
        things = Things(ids)
        things._lookup_primary_signal_endpoint_ids()

        result = things.primary_signal_endpoint_ids
        expected_result = {2: 15, 3: 6, 4: 19, 8: 14, 10: 4492, 18760: 70773}

        self.assertEqual(result, expected_result)

    def test_lookup_primary_signal_endpoint_ids_zero(self):
        ids = [170, 318, 2909, 2910, 3885, 23490, 23504]
        things = Things(ids)
        things._lookup_primary_signal_endpoint_ids()

        result = things.primary_signal_endpoint_ids
        expected_result = {
            170: 0,
            318: 0,
            2909: 0,
            2910: 0,
            3885: 0,
            23490: 0,
            23504: 0,
        }

        self.assertEqual(result, expected_result)


class TestGetTLObservations(unittest.TestCase):
    def test_get_tl_observations_valid_ids_phnTime_false(self):
        # Setup
        ids = [2, 3, 18760]
        things = Things(ids)
        things.primary_signal_endpoint_ids = {2: 15, 3: 6, 18760: 70477}

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        # Mock data for _fetch_primary_signal_endpoint_ids()
        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 15,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 1}
                    ],
                },
                {
                    "@iot.id": 6,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 2}
                    ],
                },
                {
                    "@iot.id": 70477,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:42Z", "result": 3}
                    ],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        result = things.get_primary_signal_observations(
            ids, n_obsrvtns=1, phnTime=False
        )

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
        things.primary_signal_endpoint_ids = {2: 15, 3: 6, 18760: 70477}
        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        # Mock data for _fetch_primary_signal_endpoint_ids()
        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 15,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 1},
                        {"phenomenonTime": "2024-10-27T18:37:52Z", "result": 2},
                    ],
                },
                {
                    "@iot.id": 6,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 3},
                        {"phenomenonTime": "2024-10-27T18:37:52Z", "result": 4},
                    ],
                },
                {
                    "@iot.id": 70477,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:42Z", "result": 5},
                        {"phenomenonTime": "2024-10-27T18:37:39Z", "result": 6},
                    ],
                },
            ]

        # Set side effect for fetch_data mock
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        # Call the method under test
        result = things.get_primary_signal_observations(ids, n_obsrvtns=2, phnTime=True)

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
        things = Things([2, 3])
        things.primary_signal_endpoint_ids = {2: 15, 3: 6}

        # Create a mock FETCHER
        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {
                    "@iot.id": 15,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 1}
                    ],
                },
                {
                    "@iot.id": 6,
                    "Observations": [
                        {"phenomenonTime": "2024-10-27T18:37:55Z", "result": 2}
                    ],
                },
            ]

        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        with patch("logging.error") as mock_logging_error:
            result = things.get_primary_signal_observations(
                ids, n_obsrvtns=1, phnTime=False
            )

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
        things.primary_signal_endpoint_ids = {2: 15, 3: 6, 18760: 70477}

        mock_fetcher = MagicMock()
        things.FETCHER = mock_fetcher

        def side_effect_fetch_data(endpoint, params):
            mock_fetcher.data = [
                {"@iot.id": 15, "Observations": []},
                {"@iot.id": 6, "Observations": []},
                {"@iot.id": 70477, "Observations": []},
            ]

        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data

        with patch("logging.error") as mock_logging_error:
            result = things.get_primary_signal_observations(
                ids, n_obsrvtns=1, phnTime=False
            )

            expected_result = {}
            self.assertEqual(result, expected_result)

            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("No observations found for Datastream(15).", calls)
            self.assertIn("No observations found for Datastream(6).", calls)
            self.assertIn("No observations found for Datastream(70477).", calls)


if __name__ == "__main__":
    unittest.main()

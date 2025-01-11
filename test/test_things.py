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
        # Setting
        ids = [2, 3, 4, 8, 10, 18760]
        things = Things(ids)
        things._lookup_primary_signal_endpoint_ids()
        # Testing
        result = things.primary_signal_endpoint_ids
        expected_result = {2: 15, 3: 6, 4: 19, 8: 14, 10: 4492, 18760: 70773}
        self.assertEqual(result, expected_result)

    def test_lookup_primary_signal_endpoint_ids_zero(self):
        # Setting
        ids = [170, 318, 2909, 2910, 3885, 23490, 23504]
        things = Things(ids)
        things._lookup_primary_signal_endpoint_ids()
        # Testing
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


class TestLookUpSecondarySignalEndpointIds(unittest.TestCase):
    def test_lookup_secondary_signal_endpoint_ids_non_zero(self):
        # Setting
        ids = [4, 7, 30, 42, 181, 6519, 8211, 8180]
        things = Things(ids)
        things._lookup_secondary_signal_endpoint_ids()
        # Testing
        result = things.secondary_signal_endpoint_ids
        expected_result = {
            4: 26,
            7: 28,
            30: 4512,
            42: 12430,
            181: 87671,
            6519: 73821,
            8180: 35348,
            8211: 32212,
        }
        self.assertEqual(result, expected_result)

    def test_lookup_secondary_signal_endpoint_ids_zero(self):
        # Setting
        ids = [3, 5, 8, 265, 1044, 1045, 8475, 8479, 18250]
        things = Things(ids)
        things._lookup_secondary_signal_endpoint_ids()
        # Testing
        result = things.secondary_signal_endpoint_ids
        expected_result = {
            3: 0,
            5: 0,
            8: 0,
            265: 0,
            1044: 0,
            1045: 0,
            8475: 0,
            8479: 0,
            18250: 0,
        }
        self.assertEqual(result, expected_result)


class TestLookUpAcousticSignalEndpointIds(unittest.TestCase):
    def test_lookup_acoustic_signal_endpoint_ids_non_zero(self):
        # Setting
        ids = [1151, 1272, 3698, 4442, 4538, 4910, 7099, 13622, 17684, 18620]
        things = Things(ids)
        things._lookup_acoustic_signal_endpoint_ids()
        # Testing
        result = things.acoustic_signal_endpoints_ids
        excepted_result = {
            1151: 3008,
            1272: 2359,
            3698: 14400,
            4442: 17248,
            4538: 15037,
            4910: 17896,
            7099: 23624,
            13622: 54906,
            17684: 67294,
            18620: 70325,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_acoustic_signal_endpoint_ids_zero(self):
        # Setting
        ids = [1317, 2674, 5026, 6083, 14052, 14511, 14600, 17593, 19293, 21870]
        things = Things(ids)
        things._lookup_acoustic_signal_endpoint_ids()
        # Testing
        result = things.acoustic_signal_endpoints_ids
        excepted_result = {
            1317: 0,
            2674: 0,
            5026: 0,
            6083: 0,
            14052: 0,
            14511: 0,
            14600: 0,
            17593: 0,
            19293: 0,
            21870: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpDetectorCarEndpointIds(unittest.TestCase):
    def test_lookup_detector_car_endpoint_ids_non_zero(self):
        # Setting
        ids = [1529, 3754, 5846, 6875, 7326, 8323, 12720, 13404, 17694, 21645]
        things = Things(ids)
        things._lookup_detector_car_endpoint_ids()
        # Testing
        result = things.detector_car_endpoints_ids
        excepted_result = {
            1529: 16353,
            3754: 14009,
            5846: 39655,
            6875: 28259,
            7326: 30020,
            8323: 42417,
            12720: 51860,
            13404: 54248,
            17694: 67375,
            21645: 82581,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_detector_car_endpoint_ids_zero(self):
        # Setting
        ids = [245, 449, 811, 1620, 2001, 3534, 4474, 12402, 17209, 19318]
        things = Things(ids)
        things._lookup_detector_car_endpoint_ids()
        # Testing
        result = things.detector_car_endpoints_ids
        excepted_result = {
            245: 0,
            449: 0,
            811: 0,
            1620: 0,
            2001: 0,
            3534: 0,
            4474: 0,
            12402: 0,
            17209: 0,
            19318: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpDetectorCyclistsEndpointIds(unittest.TestCase):
    def test_lookup_detector_cyclists_endpoint_ids_non_zero(self):
        # Setting
        ids = [370, 4606, 5789, 6687, 8377, 8960, 14290, 14788, 14929, 19747]
        things = Things(ids)
        things._lookup_detector_cyclists_ids()
        # Testing
        result = things.detector_cyclists_endpoints_ids
        excepted_result = {
            370: 3415,
            4606: 15067,
            5789: 30731,
            6687: 23253,
            8377: 30540,
            8960: 31860,
            14290: 56935,
            14788: 58293,
            14929: 58832,
            19747: 75356,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_detector_cyclists_endpoint_ids_zero(self):
        # Setting
        ids = [978, 1429, 5142, 6324, 6608, 7280, 12021, 19784, 20320, 23525]
        things = Things(ids)
        things._lookup_detector_cyclists_ids()
        # Testing
        result = things.detector_cyclists_endpoints_ids
        excepted_result = {
            978: 0,
            1429: 0,
            5142: 0,
            6324: 0,
            6608: 0,
            7280: 0,
            12021: 0,
            19784: 0,
            20320: 0,
            23525: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpDetectorPedestrianEndpointIds(unittest.TestCase):
    def test_lookup_detector_pedestrian_endpoint_ids_non_zero(self):
        # Setting
        ids = [3136, 3868, 4666, 6804, 9569, 9751, 11937, 17477, 21389, 23401]
        things = Things(ids)
        things._lookup_detector_pedestrian_ids()
        # Testing
        result = things.detector_pedestrian_endpoints_ids
        excepted_result = {
            3136: 15458,
            3868: 13682,
            4666: 16288,
            6804: 24678,
            9569: 35568,
            9751: 36991,
            11937: 49528,
            17477: 66641,
            21389: 81548,
            23401: 90484,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_detector_pedestrian_endpoint_ids_zero(self):
        # Setting
        ids = [2827, 4587, 5776, 7338, 9394, 10903, 13943, 15565, 18069, 18543]
        things = Things(ids)
        things._lookup_detector_pedestrian_ids()
        # Testing
        result = things.detector_pedestrian_endpoints_ids
        excepted_result = {
            2827: 0,
            4587: 0,
            5776: 0,
            7338: 0,
            9394: 0,
            10903: 0,
            13943: 0,
            15565: 0,
            18069: 0,
            18543: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpBusPreRequestEndpointIds(unittest.TestCase):
    def test_lookup_bus_pre_request_endpoint_ids_non_zero(self):
        # Setting
        ids = [110, 255, 797, 6709, 8598, 9083, 9765, 14370, 16262, 23345]
        things = Things(ids)
        things._lookup_bus_pre_request_ids()
        # Testing
        result = things.bus_pre_request_endpoints_ids
        excepted_result = {
            110: 724,
            255: 1222,
            797: 74131,
            6709: 41291,
            8598: 42616,
            9083: 40930,
            9765: 39602,
            14370: 90188,
            16262: 62783,
            23345: 90052,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_bus_pre_request_endpoint_ids_zero(self):
        # Setting
        ids = [1212, 1428, 8597, 8720, 10144, 18340, 19390, 22254, 22335, 23063]
        things = Things(ids)
        things._lookup_bus_pre_request_ids()
        # Testing
        result = things.bus_pre_request_endpoints_ids
        excepted_result = {
            1212: 0,
            1428: 0,
            8597: 0,
            8720: 0,
            10144: 0,
            18340: 0,
            19390: 0,
            22254: 0,
            22335: 0,
            23063: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpBusRequestEndpointIds(unittest.TestCase):
    def test_lookup_bus_request_endpoint_ids_non_zero(self):
        # Setting
        ids = [4, 311, 1265, 8900, 10514, 10517, 10579, 16954, 18376, 19921]
        things = Things(ids)
        things._lookup_bus_request_ids()
        # Testing
        result = things.bus_request_endpoints_ids
        excepted_result = {
            4: 74084,
            311: 1477,
            1265: 72710,
            8900: 41883,
            10514: 45166,
            10517: 45188,
            10579: 45447,
            16954: 88285,
            18376: 69586,
            19921: 76083,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_bus_request_endpoint_ids_zero(self):
        # Setting
        ids = [2628, 2957, 5778, 6303, 7138, 10313, 12122, 15597, 16766, 19602]
        things = Things(ids)
        things._lookup_bus_request_ids()
        # Testing
        result = things.bus_request_endpoints_ids
        excepted_result = {
            2628: 0,
            2957: 0,
            5778: 0,
            6303: 0,
            7138: 0,
            10313: 0,
            12122: 0,
            15597: 0,
            16766: 0,
            19602: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpBusCheckoutEndpointIds(unittest.TestCase):
    def test_lookup_bus_checkout_endpoint_ids_non_zero(self):
        # Setting
        ids = [4, 27, 28, 29, 1145, 1227, 23343, 23362]
        things = Things(ids)
        things._lookup_bus_checkout_ids()
        # Testing
        result = things.bus_checkout_endpoints_ids
        excepted_result = {
            4: 3,
            27: 156,
            28: 171,
            29: 191,
            1145: 5746,
            1227: 3227,
            23343: 90093,
            23362: 90043,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_bus_checkout_endpoint_ids_zero(self):
        # Setting
        ids = [2, 3, 5, 1084, 1088, 10650, 12219, 23441]
        things = Things(ids)
        things._lookup_bus_checkout_ids()
        # Testing
        result = things.bus_checkout_endpoints_ids
        excepted_result = {
            2: 0,
            3: 0,
            5: 0,
            1084: 0,
            1088: 0,
            10650: 0,
            12219: 0,
            23441: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpSignalProgramEndpointIds(unittest.TestCase):
    def test_lookup_signal_program_endpoint_ids_non_zero(self):
        # Setting
        ids = [1017, 2680, 8090, 9959, 19022, 21044, 21964, 22307, 22446, 22858]
        things = Things(ids)
        things._lookup_signal_program_endpoint_ids()
        # Testing
        result = things.signal_program_endpoints_ids
        excepted_result = {
            1017: 6466,
            2680: 3976,
            8090: 27780,
            9959: 32649,
            19022: 71618,
            21044: 80272,
            21964: 83855,
            22307: 85236,
            22446: 85787,
            22858: 87502,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_signal_program_endpoint_ids_zero(self):
        # Setting
        ids = [2664, 2907, 6321, 8540, 9139, 9680, 9681, 12614, 12634, 23500]
        things = Things(ids)
        things._lookup_signal_program_endpoint_ids()
        # Testing
        result = things.signal_program_endpoints_ids
        excepted_result = {
            2664: 0,
            2907: 0,
            6321: 0,
            8540: 0,
            9139: 0,
            9680: 0,
            9681: 0,
            12614: 0,
            12634: 0,
            23500: 0,
        }
        self.assertEqual(result, excepted_result)


class TestLookUpCycleSecondEndpointIds(unittest.TestCase):
    def test_lookup_cycle_second_endpoint_ids_non_zero(self):
        # Setting
        ids = [445, 2679, 2908, 3283, 3788, 4824, 10413, 20684, 23123, 23535]
        things = Things(ids)
        things._lookup_cycle_second()
        # Testing
        result = things.cycle_second_endpoints_ids
        excepted_result = {
            445: 654,
            2679: 6443,
            2908: 5115,
            3283: 10821,
            3788: 31111,
            4824: 31397,
            10413: 44884,
            20684: 78788,
            23123: 89135,
            23535: 91034,
        }
        self.assertEqual(result, excepted_result)

    def test_lookup_cycle_second_endpoint_ids_zero(self):
        # Setting
        ids = [2577, 2664, 3885, 4197, 5839, 8540, 17250, 17880, 21254, 23487]
        things = Things(ids)
        things._lookup_cycle_second()
        # Testing
        result = things.cycle_second_endpoints_ids
        excepted_result = {
            2577: 0,
            2664: 0,
            3885: 0,
            4197: 0,
            5839: 0,
            8540: 0,
            17250: 0,
            17880: 0,
            21254: 0,
            23487: 0,
        }
        self.assertEqual(result, excepted_result)


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
        result = things.get_primary_signal_observations(n_obsrvtns=1, phnTime=False)
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
        result = things.get_primary_signal_observations(n_obsrvtns=2, phnTime=True)
        # Expected result
        expected_result = {
            2: [["2024-10-27T18:37:55Z", 1], ["2024-10-27T18:37:52Z", 2]],
            3: [["2024-10-27T18:37:55Z", 3], ["2024-10-27T18:37:52Z", 4]],
            18760: [["2024-10-27T18:37:42Z", 5], ["2024-10-27T18:37:39Z", 6]],
        }
        # Assert
        self.assertEqual(result, expected_result)

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

        # Testing
        mock_fetcher.fetch_data.side_effect = side_effect_fetch_data
        with patch("logging.error") as mock_logging_error:
            result = things.get_primary_signal_observations(n_obsrvtns=1, phnTime=False)
            expected_result = {}
            self.assertEqual(result, expected_result)
            calls = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("No observations found for Datastream(15).", calls)
            self.assertIn("No observations found for Datastream(6).", calls)
            self.assertIn("No observations found for Datastream(70477).", calls)


if __name__ == "__main__":
    unittest.main()

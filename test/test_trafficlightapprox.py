from unittest.mock import MagicMock, patch
from tldhamburg.control.trafficlightapprox import TrafficLightApprox
from datetime import datetime
import numpy as np
import unittest


class TestTrafficLightApprox(unittest.TestCase):

    @patch("tldhamburg.control.trafficlightapprox.Things")
    def test_mean_light_phases_valid_input(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance
        mock_observations = {
            1: [
                ["2024-12-13T17:26:51Z", 1],
                ["2024-12-13T17:26:48Z", 2],
                ["2024-12-13T17:26:13Z", 3],
                ["2024-12-13T17:26:12Z", 4],
                ["2024-12-13T17:25:16Z", 1],
                ["2024-12-13T17:25:13Z", 2],
                ["2024-12-13T17:25:03Z", 3],
                ["2024-12-13T17:25:02Z", 4],
                ["2024-12-13T17:24:46Z", 1],
                ["2024-12-13T17:24:43Z", 2],
                ["2024-12-13T17:24:33Z", 3],
                ["2024-12-13T17:24:32Z", 4],
            ]
        }
        mock_thing_instance.get_primary_signal_observations.return_value = (
            mock_observations
        )
        result = TrafficLightApprox.mean_light_phases(1, 8)
        excepted_result = (np.float64(21.333333333333332), np.float64(37.0))
        self.assertEqual(excepted_result, result)

    @patch("tldhamburg.control.trafficlightapprox.Things")
    def test_mean_light_phases_valid_input_stddev(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance
        mock_observations = {
            1: [
                ["2024-12-13T17:26:51Z", 1],
                ["2024-12-13T17:26:48Z", 2],
                ["2024-12-13T17:26:13Z", 3],
                ["2024-12-13T17:26:12Z", 4],
                ["2024-12-13T17:25:16Z", 1],
                ["2024-12-13T17:25:13Z", 2],
                ["2024-12-13T17:25:03Z", 3],
                ["2024-12-13T17:25:02Z", 4],
                ["2024-12-13T17:24:46Z", 1],
                ["2024-12-13T17:24:43Z", 2],
                ["2024-12-13T17:24:33Z", 3],
                ["2024-12-13T17:24:32Z", 4],
            ]
        }
        mock_thing_instance.get_primary_signal_observations.return_value = (
            mock_observations
        )
        result = TrafficLightApprox.mean_light_phases(1, 12, True)
        excepted_result = (
            np.float64(21.333333333333332),
            np.float64(11.785113019775793),
            np.float64(37.0),
            np.float64(20.0),
        )
        self.assertEqual(excepted_result, result)

    @patch("tldhamburg.control.trafficlightapprox.Things")
    def test_next_switch_green(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance
        mock_observations = {
            1: [
                ["2024-12-13T17:26:51Z", 1],
                ["2024-12-13T17:26:48Z", 2],
                ["2024-12-13T17:26:13Z", 3],
                ["2024-12-13T17:26:12Z", 4],
                ["2024-12-13T17:25:16Z", 1],
                ["2024-12-13T17:25:13Z", 2],
                ["2024-12-13T17:25:03Z", 3],
                ["2024-12-13T17:25:02Z", 4],
                ["2024-12-13T17:24:46Z", 1],
                ["2024-12-13T17:24:43Z", 2],
                ["2024-12-13T17:24:33Z", 3],
                ["2024-12-13T17:24:32Z", 4],
            ]
        }
        mock_thing_instance.get_primary_signal_observations.return_value = (
            mock_observations
        )
        result = TrafficLightApprox.approx_next_switch(1)
        expeted_result = (datetime(2024, 12, 13, 17, 27, 28), "green")
        self.assertEqual(result, expeted_result)

    @patch("tldhamburg.control.trafficlightapprox.Things")
    def test_next_switch_red(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance
        mock_observations = {
            1: [
                ["2024-12-13T17:50:20Z", 3],
                ["2024-12-13T17:50:19Z", 4],
                ["2024-12-13T17:49:04Z", 1],
                ["2024-12-13T17:49:01Z", 2],
                ["2024-12-13T17:48:51Z", 3],
                ["2024-12-13T17:48:50Z", 4],
                ["2024-12-13T17:47:26Z", 1],
                ["2024-12-13T17:47:23Z", 2],
                ["2024-12-13T17:47:13Z", 3],
                ["2024-12-13T17:47:12Z", 4],
                ["2024-12-13T17:46:18Z", 1],
                ["2024-12-13T17:46:15Z", 2],
            ]
        }
        mock_thing_instance.get_primary_signal_observations.return_value = (
            mock_observations
        )
        result = TrafficLightApprox.approx_next_switch(1)
        expected_result = (datetime(2024, 12, 13, 17, 50, 33), "red")
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()

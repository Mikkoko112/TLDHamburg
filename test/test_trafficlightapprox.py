from unittest.mock import MagicMock, patch
from tldhamburg.control.evaluation.trafficlightapprox import TrafficLightApprox
from datetime import datetime, timezone
from scipy import stats
import numpy as np
import unittest


class TestTrafficLightApprox(unittest.TestCase):
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
    mock_observations_red = {
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

    def test_compute_confidence_interval_valid_data_95_confidence(self):
        data = np.array([14.0, 24.0, 15.0, 20.0, 20.0, 24.0])
        confidence = 0.95
        expected_mean = np.mean(data)
        expected_sem = stats.sem(data)
        expected_t = stats.t.ppf((1 + confidence) / 2, df=len(data) - 1)
        expected_margin = expected_t * expected_sem
        expected_interval = (
            expected_mean - expected_margin,
            expected_mean + expected_margin,
        )

        result = TrafficLightApprox.compute_confidence_interval(data, confidence)
        self.assertAlmostEqual(result[0], expected_interval[0], places=5)
        self.assertAlmostEqual(result[1], expected_interval[1], places=5)

    def test_compute_confidence_interval_single_data_point(self):
        data = np.array([42.0])
        confidence = 0.95
        expected_interval = (None, None)

        result = TrafficLightApprox.compute_confidence_interval(data, confidence)
        self.assertEqual(result, expected_interval)

    def test_compute_confidence_interval_high_confidence(self):
        data = np.array([5, 7, 9, 11, 13])
        confidence = 0.99
        expected_mean = np.mean(data)
        expected_sem = stats.sem(data)
        expected_t = stats.t.ppf((1 + confidence) / 2, df=len(data) - 1)
        expected_margin = expected_t * expected_sem
        expected_interval = (
            expected_mean - expected_margin,
            expected_mean + expected_margin,
        )

        result = TrafficLightApprox.compute_confidence_interval(data, confidence)
        self.assertAlmostEqual(result[0], expected_interval[0], places=5)
        self.assertAlmostEqual(result[1], expected_interval[1], places=5)

    @patch("tldhamburg.control.evaluation.trafficlightapprox.Things")
    def test_mean_light_phases_valid_input(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance

        mock_thing_instance.get_primary_signal_observations.return_value = (
            TestTrafficLightApprox.mock_observations
        )
        result = TrafficLightApprox.mean_light_phases(1, 8)
        excepted_result = (np.float64(21.333333333333332), np.float64(37.0))
        self.assertEqual(excepted_result, result)

    @patch("tldhamburg.control.evaluation.trafficlightapprox.Things")
    def test_mean_light_phases_valid_input_stddev(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance
        mock_thing_instance.get_primary_signal_observations.return_value = (
            TestTrafficLightApprox.mock_observations
        )
        result = TrafficLightApprox.mean_light_phases(1, 12, True)
        excepted_result = (
            np.float64(21.333333333333332),
            np.float64(11.785113019775793),
            np.float64(37.0),
            np.float64(20.0),
        )
        self.assertEqual(excepted_result, result)

    @patch("tldhamburg.control.evaluation.trafficlightapprox.Things")
    def test_next_switch_green(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance
        mock_thing_instance.get_primary_signal_observations.return_value = (
            TestTrafficLightApprox.mock_observations
        )
        result = TrafficLightApprox.approx_next_switch(1)
        expeted_result = (
            datetime(2024, 12, 13, 17, 27, 28, tzinfo=timezone.utc),
            "green",
        )
        self.assertEqual(result, expeted_result)

    @patch("tldhamburg.control.evaluation.trafficlightapprox.Things")
    def test_next_switch_green_confidence_intervals(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance
        mock_thing_instance.get_primary_signal_observations.return_value = (
            TestTrafficLightApprox.mock_observations
        )
        result = TrafficLightApprox.approx_next_switch(1, confidence_intevals=True)
        expeted_result = (
            datetime(2024, 12, 13, 17, 27, 28, tzinfo=timezone.utc),
            "green",
            datetime(2024, 12, 13, 17, 26, 51, tzinfo=timezone.utc),
            datetime(2024, 12, 13, 17, 31, 42, 124095, tzinfo=timezone.utc),
        )
        self.assertEqual(result, expeted_result)

    @patch("tldhamburg.control.evaluation.trafficlightapprox.Things")
    def test_next_switch_red(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance

        mock_thing_instance.get_primary_signal_observations.return_value = (
            TestTrafficLightApprox.mock_observations_red
        )
        result = TrafficLightApprox.approx_next_switch(1)
        expected_result = (
            datetime(2024, 12, 13, 17, 50, 33, tzinfo=timezone.utc),
            "red",
        )
        self.assertEqual(result, expected_result)

    @patch("tldhamburg.control.evaluation.trafficlightapprox.Things")
    def test_next_switch_red_confidence_intervals(self, mock_things_class):
        mock_thing_instance = MagicMock()
        mock_things_class.return_value = mock_thing_instance

        mock_thing_instance.get_primary_signal_observations.return_value = (
            TestTrafficLightApprox.mock_observations_red
        )
        result = TrafficLightApprox.approx_next_switch(1, confidence_intevals=True)
        expected_result = (
            datetime(2024, 12, 13, 17, 50, 33, tzinfo=timezone.utc),
            "red",
            datetime(2024, 12, 13, 17, 50, 33, tzinfo=timezone.utc),
            datetime(2024, 12, 13, 17, 50, 33, tzinfo=timezone.utc),
        )
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()

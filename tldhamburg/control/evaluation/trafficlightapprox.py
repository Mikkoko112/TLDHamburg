from typing import Tuple
from tldhamburg.backend.Things import Things
from datetime import datetime, timedelta
from scipy import stats
import numpy as np


class TrafficLightApprox:
    @staticmethod
    def compute_confidence_interval(data, confidence):
        """
        Computes the confidence interval for the mean of the data using t-distribution.

        Args:
            data (np.array): The data samples.
            confidence (float): The confidence level (0.95 for 95%).

        Returns:
            tuple: (lower_bound, upper_bound)
        Example:
            >>> from tldhamburg.control.evaluation.trafficlightapprox import TrafficLightApprox as tla
            >>> data = [13.0, 14.0, 15.5, 14.1, 13.5, 13.8]
            >>> result = tla.compute_confidence_interval(data, 0.95)
            >>> print(f"lower: {result[0]:.2f}, upper: {result[1]:.2f}")
            lower: 13.10, upper: 14.87
        """
        n = len(data)
        if n < 2:
            print("Not enough data to compute confidence interval.")
            return (None, None)
        mean = np.mean(data)
        sem = stats.sem(data)
        t_multiplier = stats.t.ppf((1 + confidence) / 2, df=n - 1)
        margin = t_multiplier * sem
        return (mean - margin, mean + margin)

    @staticmethod
    def mean_light_phases(
        thing_id: int,
        support_points: int,
        std_dev=False,
        confidence_intervals: bool = False,
        confidence_level: float = 0.95,
    ) -> Tuple[int, int] | dict:
        """
        Calculates the mean, and optionally the standard deviation and confidence intervals,
        of red and green phases based on primary signal observations for a given Thing.

        This function analyzes the primary signal observations of a traffic light, based on a Thing ID,
        to determine the durations of red and green phases. If requested it computes statistical measures,
        such as standard deviation and/or condifidence intervals.

        Args:
            thing_id (int): Thing ID
            support_points (int): Number of support points required (minimum 8).
                Determines how many recent observations to fetch.
            std_dev (bool, optional): If set to True, the function also returns the standard deviations
                of the red and green phases. Defaults to False.

        Returns:
            tuple or dict:
                If `std_dev` and `conf_intervals` are both False:
                    tuple: (mean_green_phase, mean_red_phase)
                If `std_dev` is True and `conf_intervals` is False:
                    tuple: (mean_green_phase, green_stddev, mean_red_phase, red_stddev)
                If `conf_intervals` is True (regardless of `std_dev`):
                    dict: {
                        "mean_green_phase": float,
                        "mean_red_phase": float,
                        "green_stddev": float (if `std_dev` is True),
                        "red_stddev": float (if `std_dev` is True),
                        "mean_green_phase_ci": tuple (lower, upper),
                        "mean_red_phase_ci": tuple (lower, upper),
                        "confidence_level": float
                    }
                None: If input conditions are not met or data is insufficient."""

        if support_points < 8:
            print("Support points should be atleast 8.")
            return None

        thing = Things([thing_id])
        try:
            observations = thing.get_primary_signal_observations(support_points, True)[
                thing_id
            ]
        except KeyError:
            print("No Observations found for Thing({})".format(thing_id))
            return None

        end_time = 0
        last_signal = -1
        timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
        red_phases, green_phases = list(), list()
        for time_stamp, signal in observations:
            start_time = datetime.strptime(time_stamp, timestamp_format)
            if last_signal == -1 and (signal == 1 or signal == 3):
                last_signal = signal
                end_time = start_time
                continue
            if last_signal == signal:
                last_signal = signal
                end_time = start_time
                continue

            if signal == 1 and last_signal == 3:
                time_diff = (end_time - start_time).total_seconds()
                red_phases.append(time_diff)
                last_signal = 1
                end_time = start_time
                # print("Red phase lasted:\t{} seconds".format(time_diff))
            elif signal == 3 and last_signal == 1:
                time_diff = (end_time - start_time).total_seconds()
                green_phases.append(time_diff)
                last_signal = 3
                end_time = start_time
                # print("Green phase lasted:\t{} seconds".format(time_diff))

        # Calculate means
        mean_red_phase = np.mean(red_phases)
        mean_green_phase = np.mean(green_phases)

        if not std_dev and not confidence_intervals:
            return mean_green_phase, mean_red_phase

        # If std_dev is requested
        if std_dev and not confidence_intervals:
            red_stddev = np.std(red_phases)  # Sample standard deviation
            green_stddev = np.std(green_phases)
            return mean_green_phase, green_stddev, mean_red_phase, red_stddev

        # If confidence intervals are requested (with or without std_dev)
        result = {
            "mean_green_phase": mean_green_phase,
            "mean_red_phase": mean_red_phase,
        }

        if std_dev:
            red_stddev = np.std(red_phases, ddof=1)
            green_stddev = np.std(green_phases, ddof=1)
            result["green_stddev"] = green_stddev
            result["red_stddev"] = red_stddev

        if confidence_intervals:
            red_ci_lower, red_ci_upper = TrafficLightApprox.compute_confidence_interval(
                red_phases, confidence_level
            )
            green_ci_lower, green_ci_upper = (
                TrafficLightApprox.compute_confidence_interval(
                    green_phases, confidence_level
                )
            )
            result["mean_green_phase_ci"] = (green_ci_lower, green_ci_upper)
            result["mean_red_phase_ci"] = (red_ci_lower, red_ci_upper)
            result["confidence_level"] = confidence_level
        return result

    @staticmethod
    def approx_next_switch(
        thing_id: int,
        confidence_intevals: bool = False,
        confidence_level: float = 0.95,
    ):
        """
        Approximates the next switch time and color for a specified traffic light
        (primary signal) of a given Thing ID.

        This function estimates when the next color change (from green to red or red to green)
        will occur for a given traffic light based on recent primary signal observations of
        a given Thing ID. It utilizes
        the mean durations of green and red phases, and optionally provides confidence intervals
        for these estimates.

        Args:
            thing_id (int): Thing ID.
            confidence_intervals (bool, optional): If set to True, the function also returns
                the lower and upper bounds of the confidence interval for the estimated switch time.
                Defaults to False.
            confidence_level (float, optional): The confidence level for the confidence intervals.
                Must be between 0 and 1. Defaults to 0.95.

        Returns:
            tuple or None:
                If `confidence_intervals` is False:
                    tuple: (approx_next_switch_time: datetime, next_color: str)
                If `confidence_intervals` is True:
                    tuple:
                        (approx_next_switch_time: datetime,
                        next_color: str,
                        approx_time_lower: datetime,
                        approx_time_upper: datetime)
                None: If input conditions are not met or data is insufficient.
        Example:
            >>> from TrafficLightApprox import TrafficLightApprox as tla
            >>> output = tla.approx_next_switch(2)
            >>> print(output)
            2024-12-09 16:36:04.625000

            >>> from datetime import datetime
            >>> switchtime, color, switchtime_lower, switchtime_upper = tla.approx_next_switch(11, True)
            >>> print(f"Approx switch time: {switchtime} to {color}")
            >>> print(f"Lower:\t{switchtime_lower}")
            >>> print(f"Upper:\t{switchtime_upper}")
            >>> print(f"Now:\t{datetime.utcnow()}")
            Approx switch time: 2024-12-19 20:48:28.571429+00:00 to green
            Lower:	2024-12-19 20:48:22.824046+00:00
            Upper:	2024-12-19 20:48:34.318811+00:00
            Now:	2024-12-19 20:47:09.515964
        """
        thing = Things([thing_id])
        try:
            observations = thing.get_primary_signal_observations(4, True)[thing_id]
        except KeyError:
            print("No Observations found for Thing({})".format(thing_id))
            return None

        result = TrafficLightApprox.mean_light_phases(
            thing_id=thing_id,
            support_points=32,
            confidence_intervals=True,
            confidence_level=confidence_level,
        )
        mean_time_green = result["mean_green_phase"]
        mean_green_ci = result["mean_green_phase_ci"]
        mean_time_red = result["mean_red_phase"]
        mean_red_ci = result["mean_red_phase_ci"]

        if np.isnan(mean_time_green) or np.isnan(mean_time_red):
            print("No mean time found for Thing({})".format(thing_id))
            return None

        for time_stamp, signal in observations:
            if signal == 3:  # if current_color == green
                time = datetime.fromisoformat(time_stamp)
                approx_time = datetime.fromisoformat(time_stamp) + timedelta(
                    seconds=mean_time_green
                )
                approx_time_lower = datetime.fromisoformat(time_stamp) + timedelta(
                    seconds=max(0, mean_green_ci[0])
                )
                approx_time_upper = datetime.fromisoformat(time_stamp) + timedelta(
                    seconds=max(0, mean_green_ci[1])
                )
                # Approximated time to next switch, color of next switch
                if confidence_intevals:
                    return (
                        approx_time,
                        "red",
                        approx_time_lower,
                        approx_time_upper,
                    )
                return (approx_time, "red")
            if signal == 1:  # if current_color == red
                time = datetime.fromisoformat(time_stamp)
                approx_time = datetime.fromisoformat(time_stamp) + timedelta(
                    seconds=mean_time_red
                )
                approx_time_lower = datetime.fromisoformat(time_stamp) + timedelta(
                    seconds=max(0, mean_red_ci[0])
                )
                approx_time_upper = datetime.fromisoformat(time_stamp) + timedelta(
                    seconds=max(0, mean_red_ci[1])
                )
                # Approximated time to next switch, color of next switch
                if confidence_intevals:
                    return (
                        approx_time,
                        "green",
                        approx_time_lower,
                        approx_time_upper,
                    )
                return (approx_time, "green")
        print("Currently an approximation can not be calculated.")
        return None

    @staticmethod
    def approx_next_switch_generator(thing_id: int):
        """
        Generator that yields the next switch times of a primary singal (traffic light)
        for a given Thing ID.

        Example:
            >>> gen = approx_next_switch_generator(2)
            >>> for _ in range(5):
            >>>     time, color = next(gen)
            >>>     print("{} {}".format(time, color))
            2024-12-18 10:03:08.857143 green
            2024-12-18 10:03:30.732143 red
            ...
        """
        thing = Things([thing_id])
        try:
            observations = thing.get_primary_signal_observations(4, True)[thing_id]
        except KeyError:

            print(f"No Observations found for Thing({thing_id})")
            return None

        time_green, time_red = TrafficLightApprox.mean_light_phases(
            thing_id=thing_id, support_points=32
        )
        # timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
        last_switch_time = None
        current_color = None
        for time_stamp, signal in observations:
            last_switch_time = datetime.fromisoformat(time_stamp)
            if signal == 1:
                current_color = "red"
                break
            if signal == 3:
                current_color = "green"
                break

        if last_switch_time is None:
            print("Currently an approximation can not be calculated.")
            return

        while True:
            if current_color == "green":
                # time of green phase
                switch_duration = timedelta(seconds=time_green)
                next_color = "red"
            else:
                # time of red phase
                switch_duration = timedelta(seconds=time_red)
                next_color = "green"

            last_switch_time += switch_duration
            yield (last_switch_time, next_color)
            current_color = next_color

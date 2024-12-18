from tldhamburg.backend.Things import Things
from datetime import datetime, timedelta
import numpy as np


class TrafficLightApprox:
    @staticmethod
    def mean_light_phases(thing_id: int, support_points: int, std_dev=False):
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

        mean_red_phase = np.mean(red_phases)
        mean_green_phase = np.mean(green_phases)
        if std_dev:
            red_stddev = np.std(red_phases)
            green_stddev = np.std(green_phases)
            return mean_green_phase, green_stddev, mean_red_phase, red_stddev
        return mean_green_phase, mean_red_phase

    @staticmethod
    def approx_next_switch(thing_id: int):
        """
        Example:
            >>> from TrafficLightApprox import TrafficLightApprox as tlapprox
            >>> output = tlapprox.approx_next_switch(2)
            >>> print(output)
            2024-12-09 16:36:04.625000
        """
        thing = Things([thing_id])
        try:
            observations = thing.get_primary_signal_observations(4, True)[thing_id]
        except KeyError:
            print("No Observations found for Thing({})".format(thing_id))
            return None

        time_green, time_red = TrafficLightApprox.mean_light_phases(
            thing_id=thing_id, support_points=32
        )
        for time_stamp, signal in observations:
            if signal == 3:  # if current_color == green
                switch_time = timedelta(seconds=time_green)
                approx_time = datetime.fromisoformat(time_stamp) + switch_time
                # Approximated time to next switch, color of next switch
                return (approx_time, "red")
            if signal == 1:  # if current_color == red
                switch_time = timedelta(seconds=time_red)
                approx_time = datetime.fromisoformat(time_stamp) + switch_time
                # Approximated time to next switch, color of next switch
                return (approx_time, "green")
        print("Currently an approximation can not be calculated.")
        return None

    @staticmethod
    def approx_next_switch_generator(thing_id: int):
        """
        Generator that yields the next switch times for a given Thing ID.

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
            return

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

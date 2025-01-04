import unittest
import logging
from unittest.mock import MagicMock, patch
from tldhamburg.frontend.Navigation import Navigation
from tldhamburg.frontend.position import Position
from pathlib import Path
import warnings

class TestNavigation(unittest.TestCase):
    def setUp(self):
        # Setup
        self.pos = Position()
        path = f"{Path.cwd().parent}/schnittstelle"
        self.navigate = Navigation(path=path)
        self.test_routes = [
            #[[9.98373,53.564093], [9.974259,53.567634]],
            [[9.927325,53.597382], [9.931858,53.598495]]
        ]
    
    def test_iterate_along_route(self):
        for test_route in self.test_routes:
            departure, destination = test_route
            self.navigate.create_route(departure, destination)
            for i in range(0, len(self.navigate.way_points)):
                if i == 0:
                    self.navigate.start_navigation(self.pos)
                    # Valid navigation texts
                    for navigation_text in self.navigate.remaining_nav_instr_texts:
                        with self.assertWarns(UserWarning):
                            if " None" in navigation_text:
                                warnings.warn(
                                    f"Navigation text contains 'None': {navigation_text}",
                                    UserWarning
                                )
                lat, lon = self.navigate.way_points[i]
                self.pos.set_pos(lat,lon)
                self.navigate.update_route(self.pos)

                # check data is in valid ranges
                logging.info(f"current waypoint index: {self.navigate.current_way_point_index}")

                # number of waypoints is correct
                result = self.navigate.current_way_point_index <= len(self.navigate.way_points)-1
                self.assertEqual(result, True)

                # speed limits are in certain range
                # TODO unbegrenzt auf Autobahnen, was ist der Rückgabewert?
                result = ((self.navigate.current_speed_limit <= 130
                        or self.navigate.current_speed_limit == "unlimited")
                        and self.navigate.current_speed_limit is not None)
                self.assertEqual(result, True)

                # distance calculation returns positive numbers
                result = (self.navigate.remaining_distance >= 0 
                    and self.navigate.remaining_distance <= 999999 
                    and self.navigate.remaining_distance is not None)
                self.assertEqual(result, True)

                # progress bar has values between 0 and 1,
                value = self.navigate.current_progress_next_tl
                result = value >= 0 
                if result == True:
                    result = value <= 1
                    # value == 1 can only occure at a traffic light
                    if value == 1:
                        result = self.navigate.current_way_point_index in list(self.navigate.trafficlights.items())
                self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()
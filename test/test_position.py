import unittest
from unittest.mock import MagicMock, patch
from tldhamburg.frontend.position import Position

class TestPosition(unittest.TestCase):
    def test_position(self):
        # Setup
        pos = Position()

        def test_set_pos(self):
            # Setup
            result = pos.set_pos(lat=9.98986339569092,lon=53.5612106323242)
            
            # Expected result
            expected_result = (9.98986339569092,53.5612106323242)

            # Assert
            self.assertEqual(result, expected_result)

        def test_set_coordinates(coordinates):
            # Setup
            result = tuple(pos.set_coordinates(coordinates=(9.987,53.123)))

            # Expected result
            expected_result = (9.987,53.123)

            # Assert
            self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
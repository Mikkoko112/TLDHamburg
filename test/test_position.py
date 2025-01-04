import unittest
from unittest.mock import MagicMock, patch
from tldhamburg.frontend.position import Position

class TestPosition(unittest.TestCase):
    def setUp(self):
        # Setup
        self.pos = Position()

    def test_set_pos(self):
        # Setup
        result = self.pos.set_pos(lat=9.98986339569092,lon=53.5612106323242)
        
        # Expected result
        expected_result = (9.98986339569092,53.5612106323242)

        # Assert
        self.assertEqual(result, expected_result)

    def test_set_coordinates(self):
        # Setup
        coordinates = (9.987, 53.123)
        result = tuple(self.pos.set_coordinates(coordinates))

        # Expected result
        expected_result = (9.987, 53.123)

        # Assert
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
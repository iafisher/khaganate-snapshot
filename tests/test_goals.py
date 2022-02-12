import unittest
from datetime import date

from base.goals import get_start_of_quarter


class GoalsTests(unittest.TestCase):
    def test_get_start_of_quarter(self):
        self.assertEqual(get_start_of_quarter(date(2022, 1, 1)), date(2022, 1, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 2, 1)), date(2022, 1, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 3, 1)), date(2022, 1, 1))

        self.assertEqual(get_start_of_quarter(date(2022, 4, 1)), date(2022, 4, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 5, 1)), date(2022, 4, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 6, 1)), date(2022, 4, 1))

        self.assertEqual(get_start_of_quarter(date(2022, 7, 1)), date(2022, 7, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 8, 1)), date(2022, 7, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 9, 1)), date(2022, 7, 1))

        self.assertEqual(get_start_of_quarter(date(2022, 10, 1)), date(2022, 10, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 11, 1)), date(2022, 10, 1))
        self.assertEqual(get_start_of_quarter(date(2022, 12, 1)), date(2022, 10, 1))

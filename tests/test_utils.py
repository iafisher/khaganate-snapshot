import unittest
from datetime import date, time

from base import utils
from base.utils import KgDate


class KgDateTests(unittest.TestCase):
    def test_isoformat(self):
        self.assertEqual(str(KgDate(year=2021, month=7)), "2021-07")
        self.assertEqual(str(KgDate(year=2021, month=7, day=4)), "2021-07-04")
        self.assertEqual(str(KgDate(year=2021, month=7, day=24)), "2021-07-24")
        self.assertEqual(str(KgDate(year=2021, month=11, day=6)), "2021-11-06")

    def test_plus_years(self):
        self.assertEqual(
            KgDate(year=2021, month=1).plus(years=10), KgDate(year=2031, month=1)
        )

    def test_plus_months(self):
        self.assertEqual(
            KgDate(year=2021, month=1).plus(months=1), KgDate(year=2021, month=2)
        )
        self.assertEqual(
            KgDate(year=2021, month=1).plus(months=12), KgDate(year=2022, month=1)
        )
        self.assertEqual(
            KgDate(year=2021, month=1).plus(months=15), KgDate(year=2022, month=4)
        )
        self.assertEqual(
            KgDate(year=2021, month=1).plus(months=120), KgDate(year=2031, month=1)
        )

    def test_plus_days(self):
        self.assertEqual(
            KgDate(year=2021, month=1, day=1).plus(days=1),
            KgDate(year=2021, month=1, day=2),
        )
        self.assertEqual(
            KgDate(year=2021, month=1, day=27).plus(days=5),
            KgDate(year=2021, month=2, day=1),
        )
        self.assertEqual(
            KgDate(year=2021, month=12, day=15).plus(days=20),
            KgDate(year=2022, month=1, day=4),
        )

    def test_minus_years(self):
        self.assertEqual(
            KgDate(year=2021, month=1).minus(years=10), KgDate(year=2011, month=1)
        )

    def test_minus_months(self):
        self.assertEqual(
            KgDate(year=2021, month=4).minus(months=1), KgDate(year=2021, month=3)
        )
        self.assertEqual(
            KgDate(year=2021, month=1).minus(months=1), KgDate(year=2020, month=12)
        )
        self.assertEqual(
            KgDate(year=2021, month=1).minus(months=15), KgDate(year=2019, month=10)
        )
        self.assertEqual(
            KgDate(year=2021, month=1).minus(months=120), KgDate(year=2011, month=1)
        )
        self.assertEqual(
            KgDate(year=2022, month=2, day=1).minus(months=1),
            KgDate(year=2022, month=1, day=1),
        )

    def test_minus_days(self):
        self.assertEqual(
            KgDate(year=2021, month=1, day=7).minus(days=1),
            KgDate(year=2021, month=1, day=6),
        )
        self.assertEqual(
            KgDate(year=2021, month=1, day=1).minus(days=5),
            KgDate(year=2020, month=12, day=27),
        )
        self.assertEqual(
            KgDate(year=2021, month=11, day=15).minus(days=20),
            KgDate(year=2021, month=10, day=26),
        )


class UtilsTests(unittest.TestCase):
    def test_time_to_minutes(self):
        self.assertEqual(utils.time_to_minutes(time(1)), 60)
        self.assertEqual(utils.time_to_minutes(time(12, 30)), 12 * 60 + 30)
        self.assertEqual(
            utils.time_to_minutes(time(3, 30), normalize_pm=True), (3 + 24) * 60 + 30
        )
        self.assertEqual(
            utils.time_to_minutes(time(12, 30), normalize_pm=True), 12 * 60 + 30
        )

    def test_count_days_of_overlap(self):
        self.assertEqual(
            utils.count_days_of_overlap(
                date(2020, 4, 20),
                date(2020, 4, 25),
                date(2020, 4, 23),
                date(2020, 4, 27),
            ),
            3,
        )
        self.assertEqual(
            utils.count_days_of_overlap(
                date(2019, 4, 20),
                date(2019, 4, 25),
                date(2020, 4, 23),
                date(2020, 4, 27),
            ),
            0,
        )
        self.assertEqual(
            utils.count_days_of_overlap(
                date(2019, 4, 20),
                date(2021, 4, 25),
                date(2020, 4, 23),
                date(2020, 4, 27),
            ),
            5,
        )
        self.assertEqual(
            utils.count_days_of_overlap(
                date(2020, 4, 23),
                date(2020, 4, 27),
                date(2019, 4, 20),
                date(2021, 4, 25),
            ),
            5,
        )
        self.assertEqual(
            utils.count_days_of_overlap(
                date(2020, 9, 1), date(2020, 9, 1), date(2020, 9, 1), date(2020, 9, 1)
            ),
            1,
        )
        self.assertEqual(
            utils.count_days_of_overlap(
                date(2020, 4, 23), None, date(2020, 4, 20), date(2020, 4, 25)
            ),
            3,
        )
        self.assertEqual(
            utils.count_days_of_overlap(
                date(2020, 4, 23), date(2020, 4, 27), date(2020, 4, 20), None
            ),
            5,
        )

    def test_format_time(self):
        self.assertEqual(utils.format_time(time(hour=17, minute=37)), "5:37\xa0PM")
        self.assertEqual(utils.format_time(time(hour=7, minute=3)), "7:03\xa0AM")
        self.assertEqual(utils.format_time(time(hour=0, minute=0)), "12:00\xa0AM")
        self.assertEqual(utils.format_time(time(hour=12, minute=0)), "12:00\xa0PM")

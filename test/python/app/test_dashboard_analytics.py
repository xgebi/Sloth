import datetime
import unittest
from app.dashboard.analytics.routes import month_delta


class DashboardAnalyticsCase(unittest.TestCase):
    def test_month_delta_to_future(self):
        day = datetime.date(2021, 9, 17)
        result = month_delta(day, 1)
        self.assertEqual(result.month, 10)
        self.assertEqual(result.year, 2021)
        self.assertEqual(result.day, 17)

    def test_month_delta_to_past(self):
        day = datetime.date(2021, 9, 17)
        result = month_delta(day, -1)
        self.assertEqual(result.month, 8)
        self.assertEqual(result.year, 2021)
        self.assertEqual(result.day, 17)

    def test_month_delta_to_future_in_february(self):
        day = datetime.date(2021, 1, 31)
        result = month_delta(day, 1)
        self.assertEqual(result.month, 2)
        self.assertEqual(result.year, 2021)
        self.assertEqual(result.day, 28)


if __name__ == '__main__':
    unittest.main()

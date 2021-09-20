import unittest
from app.dashboard.routes import format_post_data, format_post_data_json


class DashboardTestCase(unittest.TestCase):
    def test_format_post_data_json(self):
        result = format_post_data_json([
            ['123', 'title', '2021-09-17T09:00', 'post']
        ])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uuid"], '123')
        self.assertEqual(result[0]["postType"], 'post')
        self.assertEqual(result[0]["title"], 'title')
        self.assertEqual(result[0]["publishDate"], '2021-09-17T09:00')

    def test_format_post_data(self):
        result = format_post_data([
            ['123', 'title', '2021-09-17T09:00', 'post']
        ])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uuid"], '123')
        self.assertEqual(result[0]["post_type"], 'post')
        self.assertEqual(result[0]["title"], 'title')
        self.assertEqual(result[0]["publish_date"], '2021-09-17T09:00')


if __name__ == '__main__':
    unittest.main()

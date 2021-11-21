import unittest
from unittest.mock import Mock
from app.authorization.authorize import authorize_rest, authorize_web


class MyTestCase(unittest.TestCase):
    def test_something(self):
        mock = Mock()

        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()

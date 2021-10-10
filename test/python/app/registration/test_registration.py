import unittest
import app

from app.registration.register import Register


class Registration(unittest.TestCase):
    def setUp(self):
        self.app = app.create_app()
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
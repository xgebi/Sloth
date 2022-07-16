import unittest

from app import create_app


class TestLogin(unittest.TestCase):
	def setUp(self):
		app = create_app()
		self.app = app.test_client()

	def tearDown(self):
		pass

	def test_keep_logged_in(self):
		pass


if __name__ == '__main__':
	unittest.main()

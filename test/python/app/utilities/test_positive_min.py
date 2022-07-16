import unittest

from app.utilities.utilities import positive_min
from app.utilities.utility_exceptions import NoPositiveMinimumException


class UtilitiesTests(unittest.TestCase):
	def test_positive_min(self):
		self.assertEqual(positive_min(5, 2, 3, 4), 2)

	def test_positive_min_floats(self):
		self.assertEqual(positive_min(5.2, 2.1, 3.9, 4.4, floats=True), 2.1)

	def test_positive_min_int_conversion(self):
		self.assertEqual(positive_min(5.2, 2.1, 3.9, 4.4), 2)

	def test_positive_min_throws_error(self):
		try:
			positive_min(-5, -2, -3, -4)
		except Exception as e:
			self.assertEqual(type(e), NoPositiveMinimumException)
			return
		self.assertEqual(False, True)


if __name__ == '__main__':
	unittest.main()

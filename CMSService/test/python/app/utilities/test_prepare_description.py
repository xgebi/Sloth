import unittest
from app.utilities.utilities import prepare_description


class TestPrepareDescription(unittest.TestCase):
	def test_description_is_filled(self):
		paragraph = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ac convallis lorem, at faucibus urna. Curabitur aliquam, libero et fringilla ultrices, magna magna aliquet enim, quis pretium purus neque rhoncus odio. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Mauris faucibus velit felis, ac scelerisque dui interdum nec."
		res = prepare_description(char_limit=161, description=paragraph, section="")
		self.assertEqual(res, paragraph)

	def test_description_is_empty(self):
		limit = 161
		paragraph = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ac convallis lorem, at faucibus urna. Curabitur aliquam, libero et fringilla ultrices, magna magna aliquet enim, quis pretium purus neque rhoncus odio. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Mauris faucibus velit felis, ac scelerisque dui interdum nec."
		res = prepare_description(char_limit=limit, description="", section={"content": paragraph})
		self.assertEqual(res, paragraph[:limit])

	def test_description_is_none(self):
		limit = 161
		paragraph = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ac convallis lorem, at faucibus urna. Curabitur aliquam, libero et fringilla ultrices, magna magna aliquet enim, quis pretium purus neque rhoncus odio. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Mauris faucibus velit felis, ac scelerisque dui interdum nec."
		res = prepare_description(char_limit=limit, description=None, section={"content": paragraph})
		self.assertEqual(res, paragraph[:limit])

	def test_description_section_empty(self):
		limit = 161
		res = prepare_description(char_limit=limit, description="", section={"content": ""})
		self.assertEqual(res, "")

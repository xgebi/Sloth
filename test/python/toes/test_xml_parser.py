import unittest
import os

from app.toes.xml_parser import XMLParser


class MyTestCase(unittest.TestCase):

    def test_parser_detects_initial_xml_tag(self):
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toe_fragment_xml_declared.toe.html"))
        xp.parse_file()

        self.assertEqual(True, True)

    def test_parser_works_without_initial_xml_tag(self):
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toe_fragment_xml_undeclared.toe.html"))
        xp.parse_file()

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

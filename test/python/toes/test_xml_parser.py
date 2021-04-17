import unittest
import os

from app.toes.root_node import RootNode
from app.toes.xml_parser import XMLParser


class MyTestCase(unittest.TestCase):

    def test_parser_detects_initial_xml_tag(self):
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "toe_fragment_xml_declared.toe.html"))
        node: RootNode = xp.parse_file()

        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].get_name(), 'toe:fragment')
        self.assertEqual(len(node.children[0].children), 0)

    def test_parser_works_without_initial_xml_tag(self):
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "toe_fragment_xml_undeclared.toe.html"))
        node: RootNode = xp.parse_file()

        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].get_name(), 'toe:fragment')
        self.assertEqual(len(node.children[0].children), 0)

    def test_importer(self):
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "toe_fragment_xml_undeclared.toe.html"))
        xp.parse_file()


if __name__ == '__main__':
    unittest.main()

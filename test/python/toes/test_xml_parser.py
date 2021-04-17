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
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "importer.toe.html"))
        node: RootNode = xp.parse_file()

        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].get_name(), 'toe:fragment')
        self.assertEqual(len(node.children[0].children), 1)
        self.assertEqual(node.children[0].children[0].get_name(), 'toe:import')
        self.assertEqual(node.children[0].children[0].attributes["file"], 'importee.toe.html')

    def test_image(self):
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "toe_image.toe.html"))
        node: RootNode = xp.parse_file()

        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].get_name(), 'toe:fragment')
        self.assertEqual(node.children[0].children[0].paired_tag, False)
        self.assertEqual(node.children[0].children[0].get_name(), "img")
        self.assertEqual(node.children[0].children[0].attributes["toe:src"], "linkToImage")
        self.assertEqual(node.children[0].children[0].attributes["toe:alt"], "descriptionText")
        self.assertEqual(node.children[0].children[0].attributes["src"], "image.png")
        self.assertEqual(node.children[0].children[0].attributes["alt"], "this is alt")
        self.assertEqual(len(node.children[0].children[0].children), 0)

    def test_link(self):
        xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "toe_link.toe.html"))
        node: RootNode = xp.parse_file()

        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].get_name(), 'toe:fragment')
        self.assertEqual(node.children[0].children[0].paired_tag, True)
        self.assertEqual(node.children[0].children[0].get_name(), "a")
        self.assertEqual(node.children[0].children[0].attributes["toe:href"], "'I override'")
        self.assertEqual(node.children[0].children[0].attributes["href"], "/link-to-nowhere")
        self.assertEqual(len(node.children[0].children[0].children), 1)
        self.assertEqual(node.children[0].children[0].children[0].content, "Link")


if __name__ == '__main__':
    unittest.main()

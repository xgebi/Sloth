import unittest
import os

from app.toes.root_node import RootNode
from app.toes.comment_node import CommentNode
from app.toes.text_node import TextNode
from app.toes.node import Node
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

	def test_text(self):
		xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "toe_text.toe.html"))
		node: RootNode = xp.parse_file()

		self.assertEqual(len(node.children), 1)
		self.assertEqual(len(node.children[0].children), 3)
		self.assertEqual(type(node.children[0].children[1]), CommentNode)
		self.assertEqual(node.children[0].children[1].content, "note strInVar shouldn't have html")
		self.assertEqual(type(node.children[0].children[0]), Node)
		self.assertEqual(node.children[0].children[0].attributes["toe:text"], "strInVar")
		self.assertEqual(type(node.children[0].children[2]), Node)
		self.assertEqual(node.children[0].children[2].attributes["toe:text"], "'I override but HTML formatting is applied <br />'")

	def test_content(self):
		xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "toe_content.toe.html"))
		node: RootNode = xp.parse_file()

		self.assertEqual(len(node.children), 1)
		self.assertEqual(len(node.children[0].children), 3)
		self.assertEqual(type(node.children[0].children[1]), CommentNode)
		self.assertEqual(node.children[0].children[1].content, "note strInVar should have html")
		self.assertEqual(type(node.children[0].children[0]), Node)
		self.assertEqual(node.children[0].children[0].attributes["toe:content"], "strInVar")
		self.assertEqual(type(node.children[0].children[2]), Node)
		self.assertEqual(node.children[0].children[2].attributes["toe:content"], "'I override <br />'")

	def test_script(self):
		xp = XMLParser(path=os.path.join(os.getcwd(), "resources", "toes", "script_inline.toe.html"))
		node: RootNode = xp.parse_file()

		self.assertEqual(len(node.children), 1)
		self.assertEqual(len(node.children[0].children), 1)
		self.assertEqual(node.children[0].children[0].get_name(), "script")
		self.assertEqual(node.children[0].children[0].attributes["toe:inline-js"], "")
		self.assertEqual(type(node.children[0].children[0].children[0]), TextNode)
		self.assertEqual(node.children[0].children[0].children[0].content.strip(), "const myVar = {{ myVar }};")


if __name__ == '__main__':
	unittest.main()

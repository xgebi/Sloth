from xml.dom import minidom
from xml.dom.minidom import Node
import xml

from pathlib import Path
import os


def render_toe(*args, template, path_to_templates, **kwargs):
	if path_to_templates is None:
		return None

	toe_engine = Toe(path_to_templates, template, kwargs)
	return toe_engine.process_tree()


	
"""
	{ "1": "ELEMENT_NODE", "2": "ATTRIBUTE_NODE", "3": "TEXT_NODE", "4": "CDATA_SECTION_NODE", "5": "ENTITY_REFERENCE_NODE", "6": "ENTITY_NODE", "7": "PROCESSING_INSTRUCTION_NODE", "8": "COMMENT_NODE", "9": "DOCUMENT_NODE", "10": "DOCUMENT_TYPE_NODE", "11": "DOCUMENT_FRAGMENT_NODE", "12": "NOTATION_NODE" }	
"""

class Toe:
	tree = {}
	new_tree = {}
	path_to_templates = ""
	template_load_error = False

	def __init__(self, path_to_templates, template, data):
		self.path_to_templates = path_to_templates

		impl = minidom.getDOMImplementation()
		doctype = impl.createDocumentType('html', None, None) 
		self.new_tree = impl.createDocument(xml.dom.XHTML_NAMESPACE, 'html', doctype)

		template_file = ""
		if template.endswith(".html") or template.endswith(".htm"):
			with open(os.path.join(path_to_templates, template)) as f:			
					template_file = str(f.read())
		else:
			self.template_load_error = True
			return

		self.tree = minidom.parseString(template_file)
		self.remove_blanks(self.tree)
		self.tree.normalize()
		self.process_tree()		
	
	def process_tree(self):
		# There can only be one root element
		if len(self.tree.childNodes) != 1:
			return None

		for node in self.tree.childNodes[0].childNodes:
			self.process_subtree(self.new_tree, node)

		return self.new_tree.toxml()[self.new_tree.toxml().find('?>') + 2:]
	
	def process_subtree(self, new_tree_parent, tree):
		"""
		Params:
			new_tree_parent: Document or Node object
			tree: Document or Node object
		Returns
			Document or Node object
		"""
		# check for toe attributes
		attributes = dict(tree.attributes).keys()
		for attribute in attributes:
			import pdb; pdb.set_trace()
			if attribute == 'toe:if':
				self.process_if_attribute(new_tree_parent, tree)

		# check for toe tags
		# append regular element to parent element
		for child in tree.childNodes:
			self.process_subtree(None, child)


	def process_import_tag(self, parent_element, element):
		pass

	def process_if_attribute(self, parent_element, element):
		print("if thing")

	def process_for_attribute(self, parent_element, element):
		pass

	"""
		Node.parentNode
		Node.removeChild(oldChild)
		Node.replaceChild(newChild, oldChild)
		Node.insertBefore(newChild, refChild)
	"""

	# Adapted from https://stackoverflow.com/a/16919069/6588356
	def remove_blanks(self, node):
		for x in node.childNodes:
			if x.nodeType == Node.TEXT_NODE:
				if x.nodeValue:
					x.nodeValue = x.nodeValue.strip()
			elif x.nodeType == Node.ELEMENT_NODE:
				self.remove_blanks(x)
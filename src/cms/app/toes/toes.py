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
	variables = {}

	def __init__(self, path_to_templates, template, data):
		self.path_to_templates = path_to_templates
		self.variables["top_level"] = data # this will be reworked in the future when variable scope will be implemented

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
			#self.new_tree.appendChild(
			res = self.process_subtree(self.new_tree, node)#)
			import pdb; pdb.set_trace()
			print(res)

		return self.new_tree.toxml()[self.new_tree.toxml().find('?>') + 2:]
	
	def process_subtree(self, new_tree_parent, tree):
		"""
		Params:
			new_tree_parent: Document or Node object
			tree: Document or Node object
		Returns
			Document or Node object
		"""
		# check for toe tags
		if (tree.tagName.startswith('toe:')):
			return self.process_toe_tag(new_tree_parent, tree)

		# check for toe attributes
		attributes = dict(tree.attributes).keys()
		for attribute in attributes:
			if attribute == 'toe:if':
				return self.process_if_attribute(new_tree_parent, tree)				
			if attribute == 'toe:for':
				return self.process_for_attribute(new_tree_parent, tree)				
			if attribute == 'toe:while':
				return self.process_while_attribute(new_tree_parent, tree)				

		# append regular element to parent element
		new_tree_node = self.new_tree.createElement(tree.tagName)
		for node in tree.childNodes:
			new_tree_node.appendChild(self.process_subtree(new_tree_node, node))

		return new_tree_node
		


	def process_toe_tag(self, parent_element, element):
		if element.tagName.find('import'):
			return self.process_toe_import_tag(parent_element, element)

	def process_toe_import_tag(self, parent_element, element):
		file_name = element.getAttribute('file')
		imported_tree = {}

		if file_name.endswith(".html") or file_name.endswith(".htm"):
			with open(os.path.join(self.path_to_templates, file_name)) as f:			
					imported_tree = minidom.parseString(str(f.read()))
		if type(imported_tree) is xml.dom.minidom.Document:
			self.remove_blanks(imported_tree)
			imported_tree.normalize()
		
			top_node = self.new_tree.createElement(imported_tree.childNodes[0].childNodes[0].tagName)
			for child_node in imported_tree.childNodes[0].childNodes[0].childNodes:
				import pdb; pdb.set_trace()
				top_node.appendChild(self.process_subtree(top_node, imported_tree))
			return top_node
		return None

	def process_if_attribute(self, parent_element, element):
		print("if thing")

	def process_for_attribute(self, parent_element, element):
		pass

	def process_while_attribute(self, parent_element, element):
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
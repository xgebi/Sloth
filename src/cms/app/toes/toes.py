from xml.dom import minidom
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
	path_to_templates = ""
	template_load_error = False

	def __init__(self, path_to_templates, template, data):
		self.path_to_templates = path_to_templates

		template_file = ""
		if template.endswith(".html") or template.endswith(".htm"):
			with open(os.path.join(path_to_templates, template)) as f:			
					template_file = str(f.read())
		else:
			self.template_load_error = True
			return

		self.tree = minidom.parseString(template_file)
		import pdb; pdb.set_trace()
	
	def process_tree(self):
		pass

	def process_import_tag(self, parent_element, element):
		pass

	def process_if_attribute(self, parent_element, element):
		pass

	def process_for_attribute(self, parent_element, element):
		pass
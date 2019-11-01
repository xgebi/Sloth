from xml.dom import minidom
from pathlib import Path
import os


def render_toe(*args, template, path_to_templates, **kwargs):
	if path_to_templates is None:
		return None

	template_file = ""
	if template.endswith(".html") or template.endswith(".htm"):
		with open(os.path.join(path_to_templates, template)) as f:			
				template_file = str(f.read())
	else:
		template_file = template_file

	xml_data = minidom.parseString(template_file)

	result = process_tag(*args, tag=xml_data, path=path_to_templates, **kwargs)

	return "<!DOCTYPE html>" + result.toprettyxml()[result.toprettyxml().find('?>') + 2:]

def process_tag(*args, tag, new_tree=None, parent_element=None, path=None, **kwargs):	
	if tag.nodeType == 3:
		return None

	if tag.nodeType == 9:
		new_tree = minidom.Document()
		for node in tag.childNodes:
			if node.nodeType == 1:
				return process_tag(*args, tag=tag.firstChild, parent_element=new_tree, path=path, **kwargs)
		return None

	if tag.nodeType == 1:
		if tag.tagName.find('toe') != -1:
			if len(tag.tagName) == 3:
				for node in tag.childNodes:
					result = process_tag(*args, tag=node, parent_element=new_tree, path=path, **kwargs)
					if result is not None:
						parent_element.appendChild(result)
				
			if tag.tagName.find('import') != -1:
				import pdb; pdb.set_trace()
				attrs = dict(tag.attributes.items())
				for attr in attrs.keys():
					if (attr == "file"):
						template_file = ""
						with open(os.path.join(path, attrs.get(attr))) as f:			
							template_file = str(f.read())
							print(template_file)
				return "aa"
	return new_tree


	
"""
	{ "1": "ELEMENT_NODE", "2": "ATTRIBUTE_NODE", "3": "TEXT_NODE", "4": "CDATA_SECTION_NODE", "5": "ENTITY_REFERENCE_NODE", "6": "ENTITY_NODE", "7": "PROCESSING_INSTRUCTION_NODE", "8": "COMMENT_NODE", "9": "DOCUMENT_NODE", "10": "DOCUMENT_TYPE_NODE", "11": "DOCUMENT_FRAGMENT_NODE", "12": "NOTATION_NODE" }	
"""
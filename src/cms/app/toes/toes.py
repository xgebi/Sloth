from xml.dom import minidom
from pathlib import Path
import os


def render_toe(*args, template, **kwargs):
	template_file = ""
	if template.endswith(".html") or template.endswith(".htm"):
		with open(os.path.join(os.getcwd(), 'src', 'cms', 'app', 'templates', template)) as f:			
				template_file = str(f.read())
	else:
		template_file = template_file

	xml_data = minidom.parseString(template_file)

	result = process_tag(*args, tag=xml_data, **kwargs)

	return "<!DOCTYPE html>" + result['new_tree'].toprettyxml()[result['new_tree'].toprettyxml().find('?>') + 2:]

def process_tag(*args, tag, new_tree=None, **kwargs):
	import pdb; pdb.set_trace()
	for node in tag.childNodes:
		if (node.nodeType == 3 and len(node.nodeValue))
	# does tag start with 'toe' prefix
	# does tag have toe attributes
	return {"tag": tag, "new_tree": new_tree}


	if type(tag) is minidom.Document:
		new_tree = minidom.Document()
		html_tag = new_tree.createElement('html')
		
		try:
			html_tag.setAttribute("lang", lang)
		except NameError:
			html_tag.setAttribute("lang", "en")
		new_tree.appendChild(html_tag)

	{ "1": "ELEMENT_NODE", "2": "ATTRIBUTE_NODE", "3": "TEXT_NODE", "4": "CDATA_SECTION_NODE", "5": "ENTITY_REFERENCE_NODE", "6": "ENTITY_NODE", "7": "PROCESSING_INSTRUCTION_NODE", "8": "COMMENT_NODE", "9": "DOCUMENT_NODE", "10": "DOCUMENT_TYPE_NODE", "11": "DOCUMENT_FRAGMENT_NODE", "12": "NOTATION_NODE" }
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

	import pdb; pdb.set_trace()

	return process_tag(xml_data).toprettyxml()

def process_tag(tag):
	return tag
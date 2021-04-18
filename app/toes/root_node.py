from typing import List, Dict

from app.toes.processing_node import ProcessingNode


class RootNode(ProcessingNode):
    def __init__(self, html: bool = False, doctype: str = ""):
        if html:
            attributes = {
                "doctype": "html" if len(doctype) == 0 else doctype
            }
        else:
            attributes = {
                "encoding": "utf-8",
                "xml_version": "1.0"
            }
        super(RootNode, self).__init__(
            name="xml",
            parent=None,
            attributes=attributes,
        )
        self.html = html
        self.type = ProcessingNode.ROOT
        self.children = []

    def add_child(self, child: 'Node') -> 'Node':
        child.html = self.html
        self.children.append(child)
        return child

    def to_html_string(self) -> str:
        tag = f"<!DOCTYPE {self.attributes['doctype']}>"
        for child in self.children:
            tag += child.to_html_string()
        return tag

from typing import Dict, List


class Node:
    NODE = 'node'
    ROOT = 'root'
    PROCESSING = 'processing'
    DIRECTIVE = 'directive'
    TEXT = 'text'
    CDATA_TEXT = 'cdata'

    type: str = NODE
    html: bool = False

    UNPAIRED_TAGS = ["base", "br", "meta", "hr", "img", "track", "source", "embed", "col", "input"]
    ALWAYS_PAIRED = ["script"]

    def __init__(
            self,
            *args,
            name: str = "",
            attributes: Dict = {},
            children: List['Node'] = [],
            paired_tag: bool = True,
            parent: 'Node' = None,
            **kwargs
    ) -> None:

        self._name = name
        if type(attributes) is set:
            self.attributes = {}
            for attr in attributes:
                self.attributes[attr] = ""
        else:
            self.attributes = attributes
        if paired_tag:
            self.children = children
        self._paired_tag = paired_tag
        if parent:
            self.parent = parent

    def get_name(self) -> str:
        return self._name

    def set_name(self, name):
        self._name = name
        if name in self.UNPAIRED_TAGS:
            self._paired_tag = False
        if name in self.ALWAYS_PAIRED:
            self._paired_tag = True

    def set_paired(self, paired: bool):
        if self._name in self.UNPAIRED_TAGS:
            self._paired_tag = False
        if self._name in self.ALWAYS_PAIRED:
            self._paired_tag = True

    def set_attribute(self, name: str, value: str = ""):
        self.attributes[name] = value

    def get_attribute(self, name):
        return self.attributes[name]

    def remove_attribute(self, name: str):
        del self.attributes[name]

    def add_child(self, child: 'Node'):
        if self._paired_tag:
            child.html = self.html
            self.children.append(child)

    def replace_child(self, replacee, replacer):
        self.children = [replacer if item == replacee else item for item in self.children]

    def remove_child(self, child):
        if self._paired_tag and child in self.children:
            self.children.remove(child)

    def to_html_string(self) -> str:
        tag = f"<{self._name} "
        for key in self.attributes.keys():
            tag += f"{key}=\"{self.attributes[key]}\" "
        if self._paired_tag:
            tag = tag.strip() + ">"
            for child in self.children:
                tag += child.to_html_string()
            tag += f"</{self._name}>"
        else:
            tag += "/>"

        return tag

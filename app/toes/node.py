from typing import Dict, List


class Node:
    NODE = 'node'
    ROOT = 'root'
    PROCESSING = 'processing'
    DIRECTIVE = 'directive'
    TEXT = 'text'
    COMMENT = 'comment'
    CDATA_TEXT = 'cdata'

    type: str = NODE
    html: bool = False

    UNPAIRED_TAGS = ["base", "br", "meta", "hr", "img", "track", "source", "embed", "col", "input", "link"]
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
        self.paired_tag = paired_tag
        if parent:
            self.parent = parent

    def get_name(self) -> str:
        return self._name

    def set_name(self, name):
        self._name = name

    def is_paired(self):
        if self._name not in self.ALWAYS_PAIRED:
            return self._name not in self.UNPAIRED_TAGS
        return True
    def set_paired(self, paired: bool):
        if self._name in self.UNPAIRED_TAGS:
            self.paired_tag = False
        if self._name in self.ALWAYS_PAIRED:
            self.paired_tag = True

    def set_attribute(self, name: str, value: str = ""):
        self.attributes[name] = value

    def get_attribute(self, name):
        return self.attributes[name] if name in self.attributes else None

    def has_attribute(self, name):
        return name in self.attributes

    def remove_attribute(self, name: str):
        if name in self.attributes:
            del self.attributes[name]

    def add_child(self, child: 'Node') -> 'Node':
        if self.paired_tag:
            child.html = self.html
            self.children.append(child)
        return child

    def replace_child(self, replacee, replacer):
        self.children = [replacer if item == replacee else item for item in self.children]

    def remove_child(self, child):
        if self.paired_tag and child in self.children:
            self.children.remove(child)

    def to_html_string(self, clean_toes: bool = True) -> str:
        tag = f"<{self._name} "
        for key in self.attributes.keys():
            # remove toes dtd from result
            if clean_toes and key == "xmlns:toe":
                continue
            tag += f"{key}=\"{self.attributes[key]}\" "
        if self.is_paired():
            tag = tag.strip() + ">"
            for child in self.children:
                tag += child.to_html_string()
            tag += f"</{self._name}>"
        else:
            tag += "/>"

        return tag

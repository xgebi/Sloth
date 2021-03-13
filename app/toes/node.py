from typing import Dict, List


class Node:

    def __init__(
            self,
            *args,
            name: str,
            attributes: Dict = {},
            children: List = [],
            paired_tag: bool = True,
            **kwargs
    ) -> None:

        self.name = name
        if type(attributes) is set:
            self.attributes = {}
            for attr in attributes:
                self.attributes[attr] = ""
        else:
            self.attributes = attributes
        if paired_tag:
            self.children = children
        self.paired_tag = paired_tag

    def set_attribute(self, name: str, value: str = ""):
        self.attributes[name] = value

    def remove_attribute(self, name: str):
        del self.attributes[name]

    def add_child(self, child):
        if self.paired_tag:
            self.children.append(child)

    def replace_child(self, replaced, replacee):
        self.children = [replacee if item == replaced else item for item in self.children]

    def remove_child(self, child):
        if self.paired_tag and child in self.children:
            self.children.remove(child)

    def to_xml_string(self):
        pass

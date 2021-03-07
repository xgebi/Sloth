import enum
from app.toes.node import Node
from app.toes.tree import Tree


class XmlParsingInfo:
    def __init__(self):
        self.i = 0


class STATES(enum.Enum):
    new_page = 0
    initial_node = 1
    initial_node_read_node_name = 2
    initial_node_looking_for_attribute = 3
    initial_node_attribute_name = 4
    initial_node_attribute_equals = 5
    initial_node_attribute_start = 6
    initial_node_reading_attribute_value = 7
    new_node = 7
    read_node_name = 8
    looking_for_attribute = 9
    attribute_name = 10
    attribute_value_check = 11
    reading_attribute_value = 12
    self_closing = 13
    self_closed = 14
    inside_node = 15
    closing_node = 16
    closed_node = 17


class XMLParser:
    tree: Tree

    def __init__(self, *args, path, **kwargs):
        self.tree = Tree()
        with open(path, mode="r", encoding="utf-8") as text_file:
            self.text = text_file.read()

    def parse_file(self):
        pass

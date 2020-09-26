import enum
from app.toes.node import Node
from app.toes.tree import Tree


class STATES(enum.Enum):
    new = 0
    initial_node = 1
    new_node = 2
    read_node_name = 3
    looking_for_attribute = 4
    attribute_name = 5
    attribute_value_check = 6
    reading_attribute_value = 7
    self_closing = 8
    self_closed = 9
    inside_node = 10
    closing_node = 11
    closed_node = 12


class XMLParser:
    tree: Tree

    def __init__(self, *args, path, **kwargs):
        self.tree = Tree()
        with open(path, mode="r") as text_file:
            self.text = text_file.read()

    def parse_file(self):
        mode = STATES.initial_node
        for c in self.text:
            if c == "<":
                mode = STATES.new_node
            elif mode == STATES.new_node and c == "?":
                mode = STATES.initial_node

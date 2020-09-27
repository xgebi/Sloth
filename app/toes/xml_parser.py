import enum
from app.toes.node import Node
from app.toes.tree import Tree


class STATES(enum.Enum):
    new = 0
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
        with open(path, mode="r") as text_file:
            self.text = text_file.read()

    def parse_file(self):
        mode = STATES.initial_node
        temp_attr = ""
        for c in self.text:
            if c == "<":
                mode = STATES.new_node
            elif mode == STATES.new_node and c == "?":
                mode = STATES.initial_node
            elif mode == STATES.initial_node and c.isalnum():
                mode = STATES.initial_node_read_node_name
                self.tree.type = c
            elif mode == STATES.initial_node_attribute_name and c.isalnum():
                self.text.type += c
            elif mode == STATES.initial_node_attribute_name and c == " ":
                mode = STATES.initial_node_looking_for_attribute
            elif mode == STATES.initial_node_looking_for_attribute and c.isalpha():
                mode = STATES.initial_node_read_node_name
                temp_attr = c
            elif mode == STATES.initial_node_read_node_name and c.isalnum():
                temp_attr += c
            elif mode == STATES.initial_node_read_node_name and c == "=":
                self.tree.attributes[temp_attr] = ""
                mode = STATES.initial_node_attribute_equals
            elif mode == STATES.initial_node_attribute_equals and (c == "\"" or c == "\'"):
                mode = STATES.initial_node_attribute_start
                # TODO escape characters?

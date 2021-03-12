import enum
from app.toes.node import Node
from app.toes.tree import Tree


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


class XmlParsingInfo:
    def __init__(self):
        self.i = 0
        self.state = STATES.new_page

        def move_index(self, step: int = 1):
            self.i += step


class XMLParser:
    tree: Tree

    def __init__(self, *args, path, **kwargs):
        self.tree = Tree()
        with open(path, mode="r", encoding="utf-8") as text_file:
            self.text = text_file.read()

    def parse_file(self):
        if self.text is None:
            return "Error: empty text"
        if len(self.text) == 0:
            return self.text

        result = self.text
        parsing_info = XmlParsingInfo()
        while parsing_info.i < len(result):
            if result[parsing_info.i] == "<":
                pass
            elif result[parsing_info.i] == ">":
                pass
            elif result[parsing_info.i] == "=":
                pass
            elif result[parsing_info.i] == "\"" or result[parsing_info.i] == "'":
                pass
            else:
                parsing_info.move_index()

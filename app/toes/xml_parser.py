import enum
from app.toes.node import Node
from app.toes.root_node import RootNode
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
        self.root_node = RootNode()

    def parse_file(self):
        if self.text is None:
            return "Error: empty text"
        if len(self.text) == 0:
            return self.text

        result = self.text
        parsing_info = XmlParsingInfo()
        while parsing_info.i < len(result):
            if result[parsing_info.i] == "<":
                result, parsing_info = self.parse_starting_tag_character(text=result, parsing_info=parsing_info)
            elif result[parsing_info.i] == ">":
                result, parsing_info = self.parse_ending_tag_character(text=result, parsing_info=parsing_info)
            elif result[parsing_info.i] == "=":
                result, parsing_info = self.parse_attribute_dividing_character_character(text=result, parsing_info=parsing_info)
            elif result[parsing_info.i] == "\"" or result[parsing_info.i] == "'":
                result, parsing_info = self.parse_quote_character(text=result, parsing_info=parsing_info)
            else:
                result, parsing_info = self.parse_character(text=result, parsing_info=parsing_info)

    def parse_starting_tag_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

    def parse_ending_tag_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

    def parse_attribute_dividing_character_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

    def parse_quote_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

    def parse_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

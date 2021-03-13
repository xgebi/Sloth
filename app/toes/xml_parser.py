import enum
from app.toes.node import Node
from app.toes.tree import Tree
from app.toes.toes_exceptions import XMLParsingException


class STATES(enum.Enum):
    new_page = 0
    initial_node = 1
    initial_node_read_node_name = 2
    initial_node_looking_for_attribute = 3
    initial_node_attribute_name = 4
    initial_node_attribute_equals = 5
    initial_node_attribute_start = 6
    initial_node_reading_attribute_value = 7
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
        self.current_node: Node = None

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
        if text[parsing_info.i + 1] == " ":
            parsing_info.move_index()
        elif parsing_info.state == STATES.new_page:
            if text[parsing_info.i + 1] == "?":
                parsing_info.state = STATES.initial_node_read_node_name
                parsing_info.move_index(2)
            else:
                parsing_info.state = STATES.read_node_name
                parsing_info.current_node = Node()
                self.tree.children.append(parsing_info.current_node)
                self.tree.type = 'xml'
                parsing_info.move_index()
        else:
            parsing_info.move_index()

        return text, parsing_info

    def parse_ending_tag_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

    def parse_attribute_dividing_character_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

    def parse_quote_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        return text, parsing_info

    def parse_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        if parsing_info.state == STATES.read_node_name:
            name_end = min(
                text[parsing_info.i:].find(" "),
                text[parsing_info.i:].find(">"),
                text[parsing_info.i:].find("\n")
            ) + parsing_info.i
            parsing_info.current_node.name = text[parsing_info.i: name_end]
            parsing_info.move_index(name_end)
            parsing_info.state = STATES.looking_for_attribute if text[parsing_info.i: text[parsing_info.i].find(">")] != name_end else STATES.closing_node
        elif parsing_info.state == STATES.initial_node_read_node_name:
            name_end = min(
                text[parsing_info.i:].find(" "),
                text[parsing_info.i:].find(">"),
                text[parsing_info.i:].find("\n")
            ) + parsing_info.i
            self.tree.type = text[parsing_info.i: name_end]
            parsing_info.state = STATES.initial_node_looking_for_attribute
            parsing_info.move_index(name_end)
        elif parsing_info.state == STATES.looking_for_attribute:
            if text[parsing_info.i].isalnum():
                attr_divider = text[parsing_info.i:].find("=")
                tag_end = text[parsing_info.i:].find(">")
                if tag_end == -1:
                    raise XMLParsingException("Not properly closed tag")
                if tag_end > attr_divider >= 0:
                    name = text[parsing_info.i: parsing_info.i + attr_divider]
                    attribute_value = ""
                else:
                    name = text[parsing_info.i: parsing_info.i + min(
                        text[parsing_info.i:].find(">"),
                        text[parsing_info.i:].find(" "),
                        text[parsing_info.i:].find("/>"),
                    )]
                    attribute_value = ""
                parsing_info.current_node.attributes[name] = attribute_value
        elif parsing_info.state == STATES.initial_node_looking_for_attribute:
            pass
        else:
            parsing_info.move_index()
        return text, parsing_info

    def get_attribute_value(self, text: str, parsing_info: XmlParsingInfo) -> str:
        attribute_value_start = text[parsing_info.i:].find("=") + 1 + parsing_info.i

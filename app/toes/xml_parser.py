import enum
from app.toes.node import Node
from app.toes.text_node import TextNode
from app.toes.root_node import RootNode
from app.toes.processing_node import ProcessingNode
from app.toes.directive_node import DirectiveNode
from app.toes.toes_exceptions import XMLParsingException

from app.utilities import positive_min


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
    looking_for_child_nodes = 18
    looking_for_sibling_nodes = 19
    directive_read_node_name = 21
    directive_look_for_attribute = 22
    processing_instruction_read_node_name = 23
    processing_instruction_look_for_attribute = 24


class XmlParsingInfo:
    def __init__(self):
        self.i = 0
        self.state = STATES.new_page
        self.current_node: Node = None

    def move_index(self, step: int = 1):
        self.i += step


class XMLParser:
    root_node: RootNode

    def __init__(self, *args, path, **kwargs):
        self.root_node = RootNode()
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
            else:
                result, parsing_info = self.parse_character(text=result, parsing_info=parsing_info)

    def parse_starting_tag_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        if text[parsing_info.i + 1] == " ":
            parsing_info.move_index()
        elif parsing_info.state == STATES.new_page:
            if text[parsing_info.i:].find("<?xml") == 0:
                parsing_info.current_node = self.root_node
                parsing_info.move_index(len("<?xml"))
                parsing_info.state = STATES.looking_for_attribute
            else:
                self.root_node.processing_information.append(Node(name="xml", attributes={"version": "1.0"}))
                parsing_info = self.create_new_node(text, parsing_info)
                parsing_info.state = STATES.read_node_name
        elif parsing_info.state in [
            STATES.looking_for_child_nodes,
            STATES.looking_for_sibling_nodes
        ]:
            if text[parsing_info.i:].find("<![CDATA[") == 0:
                parsing_info.move_index(len("<![CDATA["))
                if parsing_info.current_node:
                    parsing_info.current_node.children.append(
                        TextNode(
                            parent=parsing_info.current_node,
                            cdata=True,
                            text=text[parsing_info.i: text[parsing_info.i:].find("]]>")]
                        )
                    )
                else:
                    parsing_info.current_node.children.append(
                        TextNode(
                            parent=None,
                            cdata=True,
                            text=text[parsing_info.i: text[parsing_info.i:].find("]]>")]
                        )
                    )
                parsing_info.move_index(len(text[parsing_info.i:].find("]]>") + len("]]>")))
            elif text[parsing_info.i:].find("<?") == 0:
                parsing_info.state = STATES.read_node_name
                parsing_info.move_index(2)
                parsing_info.current_node = Node()
                self.root_node.processing_information.append(parsing_info.current_node)
            elif text[parsing_info.i:].find("<!") == 0:
                parsing_info.state = STATES.read_node_name
                parsing_info.move_index(2)
                parsing_info.current_node = Node()
                self.root_node.directives.append(parsing_info.current_node)
            else:
                parsing_info.state = STATES.read_node_name
                if parsing_info.current_node:
                    parsing_info.current_node.children.append(Node())
                else:
                    self.root_node.children.append(Node())
                parsing_info.move_index()
        else:
            parsing_info.move_index()

        return text, parsing_info

    def create_new_node(self, text: str, parsing_info) -> XmlParsingInfo:
        if text[parsing_info.i + 1] == "?":
            parsing_info.move_index(2)
            parsing_info.current_node = ProcessingNode(parent=parsing_info.current_node)
            return parsing_info
        elif text[parsing_info.i:].find("<![CDATA["):
            parsing_info.move_index(len("<![CDATA["))
            text_node = TextNode(
                parent=parsing_info.current_node,
                cdata=True,
                text=text[parsing_info.i: text[parsing_info.i:].find("]]>")]
            )
            parsing_info.current_node.children.append(
                text_node
            )
            parsing_info.move_index(len(text_node.text) + len("]]>"))
            return parsing_info
        elif text[parsing_info.i + 1] == "!":
            parsing_info.move_index(2)
            parsing_info.current_node = DirectiveNode(parent=parsing_info.current_node)
            return parsing_info
        else:
            parsing_info.move_index()
            parsing_info.current_node = Node(parent=parsing_info.current_node)
            return parsing_info

    def parse_ending_tag_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        if parsing_info.state == STATES.looking_for_attribute:
            if text[parsing_info.i - 1] == "/":
                parsing_info.current_node = parsing_info.current_node.parent
            parsing_info.state = STATES.looking_for_child_nodes
            parsing_info.move_index()
        else:
            parsing_info.move_index()
        return text, parsing_info

    def parse_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        if parsing_info.state == STATES.read_node_name:
            name_end = positive_min(
                text[parsing_info.i:].find(" "),
                text[parsing_info.i:].find(">"),
                text[parsing_info.i:].find("\n")
            ) + parsing_info.i
            parsing_info.current_node.name = text[parsing_info.i: name_end]
            parsing_info.move_index(len(text[parsing_info.i: name_end]))
            parsing_info.state = STATES.looking_for_attribute if text[parsing_info.i: text[parsing_info.i].find(">")] != name_end else STATES.closing_node
        elif parsing_info.state == STATES.initial_node_read_node_name:
            name_end = positive_min(
                text[parsing_info.i:].find(" "),
                text[parsing_info.i:].find(">"),
                text[parsing_info.i:].find("\n")
            ) + parsing_info.i
            self.root_node.type = text[parsing_info.i: name_end]
            parsing_info.state = STATES.initial_node_looking_for_attribute
            parsing_info.move_index(len(text[parsing_info.i: name_end]))
        elif parsing_info.state in [
            STATES.looking_for_attribute,
            STATES.initial_node_looking_for_attribute
        ]:
            if text[parsing_info.i].isalnum():
                attr_divider = text[parsing_info.i:].find("=")
                tag_end = text[parsing_info.i:].find(">")
                if tag_end == -1:
                    raise XMLParsingException("Not properly closed tag")
                if attr_divider > tag_end >= 0:
                    name = text[parsing_info.i: parsing_info.i + positive_min(
                        text[parsing_info.i:].find(">"),
                        text[parsing_info.i:].find(" "),
                        text[parsing_info.i:].find("/>"),
                    )]
                    attribute_value = ""
                else:
                    name = text[parsing_info.i: parsing_info.i + text[parsing_info.i:].find("=")]
                    attribute_value = self.get_attribute_value(text=text, parsing_info=parsing_info)
                    parsing_info.move_index(len(f"{name}='{attribute_value}'"))
                if parsing_info.state == STATES.looking_for_attribute:
                    parsing_info.current_node.attributes[name] = attribute_value
                else:
                    self.root_node.attributes[name] = attribute_value
        else:
            parsing_info.move_index()
        return text, parsing_info

    def get_attribute_value(self, text: str, parsing_info: XmlParsingInfo) -> (str):
        attribute_value_start = text[parsing_info.i:].find("=") + 1 + parsing_info.i
        j = attribute_value_start + 1
        while j < len(text):
            if text[j] == "\"" and text[j-1] != "\\":
                return text[attribute_value_start + 1: j]
            j += 1
        raise XMLParsingException("Attribute not ended")

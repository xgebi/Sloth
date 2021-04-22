import enum
import os.path

from app.toes.node import Node
from app.toes.text_node import TextNode
from app.toes.root_node import RootNode
from app.toes.comment_node import CommentNode
from app.toes.processing_node import ProcessingNode
from app.toes.directive_node import DirectiveNode
from app.toes.toes_exceptions import XMLParsingException

from app.utilities import positive_min


class STATES(enum.Enum):
    new_page = 0
    read_node_name = 8
    looking_for_attribute = 9
    looking_for_child_nodes = 18
    inside_script = 19


class XmlParsingInfo:
    def __init__(self, current_node: Node = None):
        self.i = 0
        self.state = STATES.new_page
        self.current_node: Node = current_node
        self.root_node: Node = current_node

    def move_index(self, step: int = 1):
        self.i += step


class XMLParser:

    def __init__(self, *args, path=None, template=None, base_path=None, **kwargs):
        if path is not None:
            if base_path is not None:
                path = os.path.join(base_path, path)
            with open(path, mode="r", encoding="utf-8") as text_file:
                self.text = text_file.read()
        elif template is not None:
            self.text = template

    def parse_file(self):
        if self.text is None:
            return "Error: empty text"
        if len(self.text) == 0:
            return self.text

        result = self.text
        parsing_info = XmlParsingInfo(current_node=RootNode())
        while parsing_info.i < len(result):
            if result[parsing_info.i] == "<":
                result, parsing_info = self.parse_starting_tag_character(text=result, parsing_info=parsing_info)
            elif result[parsing_info.i] == ">":
                result, parsing_info = self.parse_ending_tag_character(text=result, parsing_info=parsing_info)
            elif result[parsing_info.i].isspace():

                parsing_info.move_index()
            else:
                result, parsing_info = self.parse_character(text=result, parsing_info=parsing_info)

        return parsing_info.root_node

    def parse_starting_tag_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        if text[parsing_info.i + 1] == " ":
            parsing_info.move_index()
        elif parsing_info.state == STATES.new_page:
            if text[parsing_info.i:].find("<?xml") == 0:
                parsing_info.move_index(len("<?xml"))
                parsing_info.state = STATES.looking_for_attribute
            elif text[parsing_info.i:].find("<!DOCTYPE") == 0:
                parsing_info.current_node.html = True
                parsing_info.current_node.attributes["doctype"] = text[len("<!DOCTYPE "):text.find(">")]
                parsing_info.state = STATES.looking_for_child_nodes
                parsing_info.move_index(text.find(">"))
            else:
                parsing_info = self.create_new_node(text, parsing_info)
                parsing_info.state = STATES.read_node_name
        elif parsing_info.state == STATES.looking_for_child_nodes:
            if text[parsing_info.i:].find("<![CDATA[") == 0:
                parsing_info.move_index(len("<![CDATA["))
                parsing_info.current_node.add_child(
                    TextNode(
                        parent=parsing_info.current_node,
                        cdata=True,
                        text=text[parsing_info.i: text[parsing_info.i:].find("]]>")]
                    )
                )
                parsing_info.move_index(len(text[parsing_info.i:].find("]]>") + len("]]>")))
            elif text[parsing_info.i:].find("<!--") == 0:
                comment_end_raw = text[parsing_info.i:].find("-->")
                if comment_end_raw == -1:
                    raise XMLParsingException("Not properly closed tag")
                comment_end = parsing_info.i + comment_end_raw
                parsing_info.current_node.add_child(CommentNode(content=text[parsing_info.i + 4: comment_end].strip()))
                parsing_info.move_index(len(f"{text[parsing_info.i: comment_end]}-->"))
            elif text[parsing_info.i + 1] == "/":
                name = text[parsing_info.i + 2: parsing_info.i + 2 + text[parsing_info.i + 2:].find(">")]
                if parsing_info.current_node.get_name() == name:
                    parsing_info.current_node = parsing_info.current_node.parent
                    parsing_info.move_index(len(f"</{name}>"))
                else:
                    print(text[parsing_info.i + 1:])
                    raise XMLParsingException()
            else:
                parsing_info.state = STATES.read_node_name
                parsing_info = self.create_new_node(text=text, parsing_info=parsing_info)

        else:
            parsing_info.move_index()

        return text, parsing_info

    def create_new_node(self, text: str, parsing_info) -> XmlParsingInfo:
        if text[parsing_info.i + 1] == "?":
            parsing_info.move_index(2)
            n = ProcessingNode(parent=parsing_info.current_node)
            parsing_info.current_node.add_child(n)
            parsing_info.current_node = n
            return parsing_info
        elif text[parsing_info.i + 1] == "!":
            parsing_info.move_index(2)
            n = DirectiveNode(parent=parsing_info.current_node)
            parsing_info.current_node.add_child(n)
            parsing_info.current_node = n
            return parsing_info
        else:
            parsing_info.move_index()
            n = Node(parent=parsing_info.current_node)
            parsing_info.current_node.add_child(n)
            parsing_info.current_node = n
            parsing_info.current_node.children = []  # there was some weirdness, TODO investigate later
            parsing_info.current_node.attributes = {}
            parsing_info.state = STATES.read_node_name
            return parsing_info

    def parse_ending_tag_character(self, text: str, parsing_info: XmlParsingInfo) -> (str, XmlParsingInfo):
        if parsing_info.state == STATES.looking_for_attribute:
            if (text[parsing_info.i - 1] == "/" or not parsing_info.current_node.is_paired()) \
                    and type(parsing_info.current_node) is not RootNode:
                parsing_info.current_node.paired_tag = False
                parsing_info.current_node = parsing_info.current_node.parent

            parsing_info.state = STATES.looking_for_child_nodes

            if parsing_info.current_node.get_name().lower() != 'script':
                parsing_info.move_index()
            else:
                end_script = parsing_info.i + text[parsing_info.i + 1:].find("</script>")
                if end_script < parsing_info.i:
                    raise XMLParsingException("Attribute not ended")
                parsing_info.current_node.add_child(
                    TextNode(
                        content=text[parsing_info.i + 1:end_script]
                    )
                )
                parsing_info.move_index(len(f"{text[parsing_info.i:end_script]}</script>") + 1)
                parsing_info.current_node = parsing_info.current_node.parent
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
            parsing_info.current_node.set_name(text[parsing_info.i: name_end])
            parsing_info.move_index(len(text[parsing_info.i: name_end]))
            parsing_info.state = STATES.looking_for_attribute
        elif parsing_info.state == STATES.looking_for_attribute:
            if text[parsing_info.i].isalnum():
                attr_divider = text[parsing_info.i:].find("=")
                tag_end = text[parsing_info.i:].find(">")
                if tag_end == -1:
                    raise XMLParsingException("Not properly closed tag")
                if ((attr_divider > tag_end) and (tag_end >= 0)) or (attr_divider < 0):
                    name = text[parsing_info.i: parsing_info.i + positive_min(
                        text[parsing_info.i:].find(">"),
                        text[parsing_info.i:].find(" "),
                        text[parsing_info.i:].find("/>"),
                    )]
                    attribute_value = ""
                    parsing_info.move_index(len(f"{name}"))
                else:
                    name = text[parsing_info.i: parsing_info.i + text[parsing_info.i:].find("=")]
                    attribute_value = self.get_attribute_value(text=text, parsing_info=parsing_info)
                    parsing_info.move_index(len(f"{name}='{attribute_value}'"))
                parsing_info.current_node.attributes[name] = attribute_value
            else:
                parsing_info.move_index()
        elif parsing_info.state == STATES.looking_for_child_nodes:
            text_end_raw = text[parsing_info.i:].find("<")
            if text_end_raw == -1:
                raise XMLParsingException("Not properly closed tag")
            text_end = parsing_info.i + text_end_raw
            parsing_info.current_node.add_child(TextNode(content=text[parsing_info.i: text_end]))
            parsing_info.move_index(len(text[parsing_info.i: text_end]))
        else:
            parsing_info.move_index()
        return text, parsing_info

    def get_attribute_value(self, text: str, parsing_info: XmlParsingInfo) -> (str):
        ending_char = text[parsing_info.i + text[parsing_info.i:].find("=") + 1] if text[parsing_info.i + text[parsing_info.i:].find("=") + 1] in {"\"", "'"} else -1
        if ending_char == -1:
            raise XMLParsingException("Attribute not ended")
        j = text[parsing_info.i:].find("=") + parsing_info.i + len(f"{ending_char}")

        while j < len(text):
            j += 1
            if text[j] == ending_char and text[j - 1] != "\\":
                return text[text[parsing_info.i:].find("=") + parsing_info.i + len(f"{ending_char}") + 1: j]

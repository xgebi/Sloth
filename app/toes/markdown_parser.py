import re
import math


class ListInfo:
    indent = 2

    def __init__(self, parent=None, type=None):
        self.level = -1 if parent is None else parent.level + 1
        self.type = type
        self.parent = parent


class ParsingInfo:
    def __init__(self):
        self.i = 0
        self.list_info = ListInfo()
        self.opened_paragraph = False
        self.footnotes = []

    def move_index(self, step: int = 1):
        self.i += step


class MarkdownParser:
    def __init__(self, *args, path=None, **kwargs):
        if path:
            with open(path, mode="r", encoding="utf-8") as text_file:
                self.text = text_file.read()
        else:
            self.text = ""

    def to_html_string(self, text: str = "") -> str:
        # refactoring candidate
        if text:
            self.text = text
        if len(self.text) == 0:
            return self.text
        if self.text is None:
            return "Error: empty text"

        result = self.text
        parsing_info = ParsingInfo()
        while parsing_info.i < len(result):
            if result[parsing_info.i] == "`":
                # parse code
                result, parsing_info = self.parse_code_block(result, parsing_info)
            elif result[parsing_info.i] == '-' or result[parsing_info.i] == '*':
                # parse horizontal line, unordered list, bold and italic
                if result[parsing_info.i: parsing_info.i + 3] == '---':
                    result, parsing_info = self.parse_horizontal_line(text=result, parsing_info=parsing_info)
                else:
                    result, parsing_info = self.parse_unordered_list(result, parsing_info)
            elif result[parsing_info.i].isdigit():
                # parse ordered list
                result, parsing_info = self.parse_ordered_list(result, parsing_info)
            elif result[parsing_info.i] == "[":
                # parse footnote and link
                parsing_info.move_index()
            elif len(result) > parsing_info.i + 2 and result[parsing_info.i:parsing_info.i + 2] == "![":
                # parse image
                result, parsing_info = self.parse_image(text=result, parsing_info=parsing_info)
            elif result[parsing_info.i] == "#":
                # parse list
                if parsing_info.i == 0 or result[parsing_info.i - 1] != "\\":
                    result, parsing_info = self.parse_headline(text=result, parsing_info=parsing_info)
                else:
                    parsing_info.move_index()
            elif not result[parsing_info.i].isspace():
                # parse paragraph
                result, parsing_info = self.parse_paragraph(text=result, parsing_info=parsing_info)
            elif result[parsing_info.i] == '\n':
                # check for endings and stuff
                if len(result) > parsing_info.i + 1 and result[parsing_info.i + 1] == '\n':
                    result, parsing_info = self.end_tags(text=result, parsing_info=parsing_info)
                else:
                    parsing_info.move_index()
            else:
                # deal with the rest
                parsing_info.move_index()

        # clean up after parse
        result, parsing_info = self.end_tags(text=result, parsing_info=parsing_info)

        """
        result = self.parse_link(result)
        result = self.parse_footnotes(result)
        result = self.parse_italic_bold(result)
        result = self.parse_escaped_characters(result)"""

        return result

    def parse_horizontal_line(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
        text = f"{text[parsing_info.i - 1:]}<hr />{text[parsing_info.i + 3:]}"
        parsing_info.i += len("<hr />")
        return text, parsing_info

    def parse_headline(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
        level = len(text[parsing_info.i:text[parsing_info.i:].find(" ") + + parsing_info.i])
        end_of_line = text[parsing_info.i:].find("\n")
        tail = text[end_of_line + parsing_info.i:] if end_of_line >= 0 else ""
        if text[parsing_info.i:text[parsing_info.i:].find("\n") + parsing_info.i].find("{#") > -1 \
                or (text[parsing_info.i:].find("\n") == -1 and text[parsing_info.i:].find("{#") > -1):
            id_start = text[parsing_info.i:].find("{#")
            id = text[id_start + parsing_info.i + 3: text[parsing_info.i:].find("}") + parsing_info.i - 1]
            content = text[parsing_info.i + level + 1: text[parsing_info.i:].find(" {#") + parsing_info.i]
            text = f"{text[:parsing_info.i]}<h{level} id=\"{id}\">{content}</h{level}>{tail}"
            parsing_info.i += len(f"<h{level} id=\"{id}\">")
        else:
            old_length = len(text[parsing_info.i: text[parsing_info.i:].find("\n") + parsing_info.i])
            content = text[parsing_info.i + level + 1: text[parsing_info.i:].find("\n") + parsing_info.i] if text[
                                                                                                             parsing_info.i:].find(
                "\n") >= 0 else text[parsing_info.i + level:]
            text = f"{text[:parsing_info.i]}<h{level}>{content.strip()}</h{level}>{tail}"
            parsing_info.i += len(f"<h{level}>")

        return text, parsing_info

    def parse_ordered_list(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
        line_start = text[:parsing_info.i].rfind("\n") + 1
        line_end = text[parsing_info.i:].find("\n") + parsing_info.i if text[parsing_info.i:].find(
            "\n") != -1 else len(text)
        line = text[line_start: line_end]
        numeric_list_pattern = re.compile('^(\d+\. )')
        if numeric_list_pattern.match(line.strip()):
            content_start = parsing_info.i + line.strip().find(' ') + 1
            if parsing_info.list_info.level == -1:
                text = f"{text[:line_start]}<ol>\n<li>{text[content_start:]}"
                parsing_info.i += len("<ol>\n<li>")
                parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type=1)
            elif parsing_info.list_info.level == 0:
                if len(text[line_start: parsing_info.i]) > 0:
                    ListInfo.indent = len(text[line_start: parsing_info.i])
                    text = f"{text[:line_start]}<ol><li>{text[content_start:]}"
                    new_list = ListInfo(parent=parsing_info.list_info, type=1)
                    parsing_info.list_info = new_list
                    parsing_info.i += len("<ol><li>") - ListInfo.indent
                else:
                    text = f"{text[:line_start]}</li><li>{text[content_start:]}"
                    parsing_info.i += len("</li><li>")
            else:
                level = math.ceil(len(text[line_start: parsing_info.i]) / ListInfo.indent)
                if level == parsing_info.list_info.level:
                    text = f"{text[:line_start]}</li><li>{text[content_start:]}"
                    parsing_info.i += len("</li><li>") - (level * ListInfo.indent)
                elif level < parsing_info.list_info.level:
                    content_tail = text[content_start:]
                    text_head = text[:line_start]

                    while level < parsing_info.list_info.level:
                        if type(parsing_info.list_info.type) is int:
                            text_head = f"{text_head}</li></ol>"
                        else:
                            text_head = f"{text_head}</li></ul>"
                        parsing_info.list_info = parsing_info.list_info.parent

                    if type(parsing_info.list_info.type) is int:
                        text = f"{text_head}</li><li>{content_tail}"
                    else:
                        text = f"{text_head}</li><li>{content_tail}"
                    parsing_info.i += (len(text_head) - len(text[:line_start])) - (level * ListInfo.indent) + len(
                        "</li><li>")
                elif level > parsing_info.list_info.level:
                    text = f"{text[:line_start]}<ol><li>{text[content_start:]}"
                    parsing_info.i += len("</ol><li>") - (level * ListInfo.indent) - 1
                    parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type=1)
        else:
            return self.parse_paragraph(text=text, parsing_info=parsing_info)

        return text, parsing_info

    def parse_unordered_list(self, text: str, parsing_info: ParsingInfo):
        line_start = text[:parsing_info.i].rfind("\n") + 1
        line_end = text[parsing_info.i:].find("\n") + parsing_info.i if text[parsing_info.i:].find("\n") != -1 else len(
            text)
        line = text[line_start: line_end]
        points_list_pattern = re.compile('^([\-|\*] )')
        if points_list_pattern.match(line.strip()):
            content_start = parsing_info.i + line.strip().find(' ') + 1
            if parsing_info.list_info.level == -1:
                text = f"{text[:line_start]}<ul>\n<li>{text[content_start:]}"
                parsing_info.i += len("<ul>\n<li>")
                parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type='a')
            elif parsing_info.list_info.level == 0:
                if len(text[line_start: parsing_info.i]) > 0:
                    ListInfo.indent = len(text[line_start: parsing_info.i])
                    text = f"{text[:line_start]}<ul><li>{text[content_start:]}"
                    new_list = ListInfo(parent=parsing_info.list_info, type='a')
                    parsing_info.list_info = new_list
                    parsing_info.i += len("<ul><li>") - ListInfo.indent
                else:
                    text = f"{text[:line_start]}</li><li>{text[content_start:]}"
                    parsing_info.i += len("</li><li>")
            else:
                level = math.ceil(len(text[line_start: parsing_info.i]) / ListInfo.indent)
                if level == parsing_info.list_info.level:
                    text = f"{text[:line_start]}</li><li>{text[content_start:]}"
                    parsing_info.i += len("</li><li>") - (level * ListInfo.indent)
                elif level < parsing_info.list_info.level:
                    content_tail = text[content_start:]
                    text_head = text[:line_start]

                    while level < parsing_info.list_info.level:
                        if type(parsing_info.list_info.type) is int:
                            text_head = f"{text_head}</li></ol>"
                        else:
                            text_head = f"{text_head}</li></ul>"
                        parsing_info.list_info = parsing_info.list_info.parent

                    if type(parsing_info.list_info.type) is int:
                        text = f"{text_head}</li><li>{content_tail}"
                    else:
                        text = f"{text_head}</li><li>{content_tail}"
                    parsing_info.i += (len(text_head) - len(text[:line_start])) - (level * ListInfo.indent) + len(
                        "</li><li>")
                elif level > parsing_info.list_info.level:
                    text = f"{text[:line_start]}<ul><li>{text[content_start:]}"
                    parsing_info.i += len("</ul><li>") - (level * ListInfo.indent) - 1
                    parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type='a')
        else:
            parsing_info.move_index()
        return text, parsing_info

    def end_tags(self, text: str, parsing_info: ParsingInfo):
        if parsing_info.list_info.level != -1:
            while parsing_info.list_info.level != -1:
                text = f"{text[:parsing_info.i]}</li>\n</ol>\n{text[parsing_info.i + 1:]}" if type(
                    parsing_info.list_info.type) is int else f"{text[:parsing_info.i]}</li>\n</ul>\n{text[parsing_info.i + 1:]}"
                parsing_info.list_info = parsing_info.list_info.parent
                parsing_info.i += len("</li>\n</ol>")
        else:
            parsing_info.move_index()
        return text, parsing_info

    def parse_paragraph(self, text: str, parsing_info: ParsingInfo):
        line_start = text[:parsing_info.i].rfind("\n\n") + 2 if text[:parsing_info.i].rfind("\n\n") >= 0 else 0
        alt_line_start = text[:parsing_info.i].rfind(">\n") + 2 if text[:parsing_info.i].rfind(">\n") >= 0 else 0

        if line_start < alt_line_start:
            line_start = alt_line_start

        if text[line_start:].startswith("<"):
            parsing_info.move_index()
            return text, parsing_info

        j = parsing_info.i
        while j < len(text):
            line_end = text[j:].find("\n\n") + j if text[j:].find("\n\n") != -1 else len(text)
            alt_line_end = text[j:].find("\n") + j if text[j:].find("\n") != -1 else len(text)

            if line_end == alt_line_end:
                line = text[line_start: line_end]
                text = f"{text[:line_start]}<p>{line}</p>{text[line_end:]}"
                parsing_info.move_index(len("<p>"))
                break
            elif "#-*".find(text[alt_line_end + 1]) >= 0:
                line = text[line_start: alt_line_end]
                text = f"{text[:line_start]}<p>{line}</p>{text[alt_line_end:]}"
                parsing_info.move_index(len("<p>"))
                break
            elif text[alt_line_end + 1].isdigit():
                j = alt_line_end + 2
                while j < len(text) and text[j].isdigit():
                    j += 1
                if text[j] == ".":
                    line = text[line_start: alt_line_end]
                    text = f"{text[:line_start]}<p>{line}</p>{text[alt_line_end:]}"
                    parsing_info.move_index(len("<p>"))
                    break
                if j == len(text):
                    text = f"{text[:line_start]}<p>{text[line_start]}:</p>"
                    parsing_info.move_index(len("<p>"))
                    break
            else:
                j += (alt_line_end - j) + 1

        return text, parsing_info

    def parse_code_block(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
        if (parsing_info.i - 1 < 0 or text[parsing_info.i - 1] == " " or text[parsing_info.i - 1] == "\n") \
                and text[parsing_info.i + 1] != "`":
            j = text[parsing_info.i + 1:].find("`") + (parsing_info.i + 1)
            if text[j + 1] != "`":
                replacement = f"<span class='code'>{text[parsing_info.i + 1:j]}</span>"
                if parsing_info.i == 0:
                    text = replacement + text[j + 1:]
                else:
                    text = text[:parsing_info.i] + replacement + text[j + 1:]
                parsing_info.i += (len(replacement) - 2)
            else:
                parsing_info.move_index()
        elif (parsing_info.i - 1 < 0 or text[parsing_info.i - 1] == "\n") and text[parsing_info.i + 1] == "`" and text[
            parsing_info.i + 2] == "`":
            j = text[parsing_info.i + 3:].find("```") + (parsing_info.i + 3)
            first_line_end = text[parsing_info.i + 3:].find("\n") + (parsing_info.i + 3)
            lang = text[parsing_info.i + 3: first_line_end]
            if j != -1:
                replacement = f"<pre><code class='language-{lang}'>{text[first_line_end + 1:j]}</code></pre>"
                if parsing_info.i == 0:
                    text = replacement + text[j + 3:]
                else:
                    text = text[:parsing_info.i - 1] + replacement + text[j + 3:]
                parsing_info.i += len(replacement)
        else:
            parsing_info.move_index()

        return text, parsing_info

    def parse_footnotes(self, text: str) -> str:
        footnote_pattern = r"\[\d+\. .+?\]"
        re_fp = re.compile(footnote_pattern)
        footnotes = re_fp.findall(text)
        list = "<ul>"
        for note in footnotes:
            index = note[1:note.find(".")]
            text = text.replace(note, f"<sup><a href='#footnote-{index}' id='footnote-link-{index}'>{index}.</a></sup>")

            list += f"<li id='footnote-{index}'>{note[note.find('. ') + 2:len(note) - 1]}"
            list += f"<a href='#footnote-link-{index}'>🔼{index}</a></li>"

        list += "</ul>"
        if len(footnotes) > 0:
            return " ".join([text, list])
        return text

    def parse_link(self, text: str) -> str:
        return re.sub(r"([^!]|^)\[([^(\d+\.)])(.*)\]\(([0-9A-z\-\_\.\~\!\*\'\(\)\;\:\@\&\=\+\$\,\/\?\%\#]+)\)",
                      "\g<1><a href='\g<4>'>\g<2>\g<3></a>", text)

    def parse_image(self, text: str, parsing_info: ParsingInfo) -> (str, ParsingInfo):
        img_pattern = re.compile("!\[(.*)]\((.*)\)")
        if img_pattern.match(text[parsing_info.i:]):
            img_info = text[
                       parsing_info.i:
                       img_pattern.match(text[parsing_info.i:]).span()[1] + parsing_info.i
                       ].split("](")
            img_code = f"<img alt=\"{img_info[0][2:]}\" src=\"{img_info[1][:len(img_info[1]) - 1]}\" />"
            text = f"{text[:parsing_info.i]}{img_code}{text[img_pattern.match(text[parsing_info.i:]).span()[1] + parsing_info.i:]}"
            parsing_info.move_index(len(img_code))
        else:
            parsing_info.move_index()
        return text, parsing_info

    def parse_italic_bold(self, text: str) -> str:
        strikethrough = re.sub(r"(~~)(.*)(~~)", "<span class='strikethrough'>\g<2></span>", text)
        bi = re.sub(r"(\*\*\*)(.*)(\*\*\*)", "<strong><em>\g<2></em></strong>", strikethrough)
        b = re.sub(r"(\*\*)(.*)(\*\*)", "<strong>\g<2></strong>", bi)
        return re.sub(r"(\*)(.*)(\*)", "<em>\g<2></em>", b)

    def parse_escaped_characters(self, text: str) -> str:
        return text

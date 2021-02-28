import re
import math


class ListInfo:
    indent = 2
    def __init__(self, parent = None, type = None):
        self.level = -1 if parent is None else parent.level + 1
        self.type = type
        self.parent = parent



class ParsingInfo:
    def __init__(self):
        self.i = 0
        self.list_info = ListInfo()


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
        while parsing_info.i < len(self.text):
            if self.text[parsing_info.i] == "`":
                result, parsing_info = self.parse_code_block(result, parsing_info)
            elif self.text[parsing_info.i] == '\-' or self.text[parsing_info.i] == '\*':
                result, parsing_info = self.parse_unordered_list(result, parsing_info)
            elif self.text[parsing_info.i].isdigit():
                result, parsing_info = self.parse_ordered_list(result, parsing_info)
            elif self.text[parsing_info.i] == '\n':
                if self.text[parsing_info.i + 1] == '\n':
                    result, parsing_info = self.end_tags(text=self.text, parsing_info=parsing_info)
                else:
                    parsing_info.i += 1
            else:
                parsing_info.i += 1

        """result = self.parse_headlines(result)
        result = self.parse_image(result)
        result = self.parse_link(result)
        result = self.parse_footnotes(result)
        result = self.parse_paragraphs(result)
        result = self.parse_italic_bold(result)
        result = self.parse_escaped_characters(result)"""

        return result

    def parse_paragraphs(self, text: str) -> str:
        lines = text.split("\n")
        result = []
        paragraph_start_pattern = re.compile('(\d+)? ?[a-zA-z\*~]+')
        for i, line in enumerate(lines):
            if len(line) > 0 and paragraph_start_pattern.match(line):
                if i != 0 and result[-1].endswith("</p>") and not \
                        (result[-1].endswith("</pre>") or result[-1].endswith("</ol>") or result[-1].endswith("</ul>")):
                    result[-1] = f"{result[-1][:result[-1].index('</p>')]} {line}</p>"
                    continue
                else:
                    line = f"<p>{line}</p>"
            result.append(line)

        return "\n".join(result)

    def parse_headlines(self, text: str) -> str:
        lines = text.split("\n")
        result = []
        headline_pattern = re.compile("\#+ ")
        for line in lines:
            match = headline_pattern.match(line)
            if len(line) > 0 and match:
                level = line[:match.end()].count("#")
                line = f"<h{level}>{line[level + 1:]}</h{level}>"
            result.append(line)
        return "\n".join(result)

    def parse_ordered_list(self, text: str, parsing_info: ParsingInfo):
        line_start = text[:parsing_info.i].rfind("\n") + 1
        line_end = text[parsing_info.i:].find("\n") + (parsing_info.i - 1) if text[parsing_info.i:].find(
            "\n") != -1 else len(text)
        line = text[line_start: line_end]
        numeric_list_pattern = re.compile('^(\d+\. )')
        if numeric_list_pattern.match(line.strip()):
            content_start = line.strip().find('.') + 2
            if parsing_info.list_info.level == -1:
                text = f"{text[:line_start]}<ol>\n<li>{text[content_start + 2:]}"
                parsing_info.i += len("<ol>\n<li>")
                parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type=1)
            elif parsing_info.list_info.level == 0:
                if len(text[line_start: parsing_info.i]) > 0:
                    ListInfo.indent = len(text[line_start: parsing_info.i])
                    text = f"{text[:line_start]}<ol><li>{text[content_start:]}"
                    parsing_info.i += len("<ol><li>")
                else:
                    text = f"{text[:line_start]}</li><li>{text[content_start:]}"
                    parsing_info.i += len("</li><li>")
            else:
                level = math.ceil(len(text[line_start: parsing_info.i]) / ListInfo.indent)
                if level == parsing_info.list_info.level:
                    text = f"{text[:line_start]}</li><li>{text[content_start:]}"
                    parsing_info.i += len("</li><li>")
                elif level < parsing_info.list_info.level:
                    if parsing_info.list_info.type.isdigit():
                        text = f"{text[:line_start]}</ol></li><li>{text[content_start:]}"
                    else:
                        text = f"{text[:line_start]}</ul></li><li>{text[content_start:]}"
                    parsing_info.i += len("</ol></li><li>")
                    parsing_info.list_info = parsing_info.list_info.parent
                elif level > parsing_info.list_info.level:
                    text = f"{text[:line_start]}<ol><li>{text[content_start:]}"
                    parsing_info.i += len("</ol><li>")
                    parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type=1)

        parsing_info.i += 4
        return text, parsing_info

    def parse_unordered_list(self, text: str, parsing_info: ParsingInfo):
        line_start = text[:parsing_info.i].rfind("\n") + 1
        line_end = text[parsing_info.i:].find("\n") + (parsing_info.i - 1) if text[parsing_info.i:].find("\n") != -1 else len(text)
        line = text[line_start: line_end]
        points_list_pattern = re.compile('^([\-|\*] )')
        if points_list_pattern.match(line.strip()):
            if parsing_info.list_info.level == -1:
                text = f"{text[:line_start]}<ul>\n<li>{text[line_start + 2:]}"
                parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type='a')
            elif parsing_info.list_info.level == 0:
                if len(text[line_start: parsing_info.i]) > 0:
                    ListInfo.indent = len(text[line_start: parsing_info.i])
                    text = f"{text[:line_start]}<ul><li>{text[line_start + 2:]}"
                    parsing_info.i += len("<ul><li>")
                else:
                    text = f"{text[:line_start]}</li><li>{text[line_start + 2:]}"
                    parsing_info.i += len("</li><li>")
            else:
                level = math.ceil(len(text[line_start: parsing_info.i]) / ListInfo.indent)
                if level == parsing_info.list_info.level:
                    text = f"{text[:line_start]}</li><li>{text[line_start + 2:]}"
                    parsing_info.i += len("</li><li>")
                elif level < parsing_info.list_info.level:
                    if parsing_info.list_info.type.isdigit():
                        text = f"{text[:line_start]}</ol></li><li>{text[line_start + 2:]}"
                    else:
                        text = f"{text[:line_start]}</ul></li><li>{text[line_start + 2:]}"
                        parsing_info.i += len("</ul></li><li>")
                    parsing_info.list_info = parsing_info.list_info.parent
                elif level > parsing_info.list_info.level:
                    text = f"{text[:line_start]}<ul><li>{text[line_start + 2:]}"
                    parsing_info.i += len("<ul><li>")
                    parsing_info.list_info = ListInfo(parent=parsing_info.list_info, type='a')

        return text, parsing_info

    def end_tags(self, text: str, parsing_info: ParsingInfo):
        return text, parsing_info

    # TODO refactor this when recoding to Rust
    def parse_list(self, text: str) -> str:
        lines = text.split("\n")
        result = []
        numeric_list_pattern = re.compile('^(\d+\. )')
        points_list_pattern = re.compile('^([\-] )')
        line_pattern = re.compile("(^( )+)?(\d\.|\-)")
        current_level = -1
        lists = []
        for i, line in enumerate(lines):
            if len(line) > 0 and numeric_list_pattern.match(line.strip()):
                if current_level == -1:
                    line = f"<ol>\n<li>{line[line.index('. ') + 2:]}"
                    current_level += 1
                    lists.append("ol")
                elif current_level > -1:
                    if current_level == (
                            len(line[:line.index(line[:line_pattern.match(line).end() - 1].strip())]) // 4):
                        line = f"</li>\n<li>{line[line.index('. ') + 2:]}"
                    elif current_level < (
                            len(line[:line.index(line[:line_pattern.match(line).end() - 1].strip())]) // 4):
                        line = f"<ol><li>{line[line.index('. ') + 2:]}"
                        current_level += 1
                        lists.append("ol")
                    else:
                        temp_line = ""
                        while current_level > (
                                len(line[:line.index(line[:line_pattern.match(line).end() - 1].strip())]) // 4):
                            temp_line += f"</li>\n</{lists[-1]}>"
                            current_level -= 1
                            lists.pop()
                        line = f"{temp_line}</li>\n<li>{line[line.index('. ') + 2:]}"
            elif len(line) > 0 and points_list_pattern.match(line.strip()):
                if current_level == -1:
                    line = f"<ul>\n<li>{line[line.index('- ') + 2:]}"
                    current_level += 1
                    lists.append("ul")
                elif current_level > -1:
                    if current_level == (len(line[:line.index(line[:line_pattern.match(line).end()].strip())]) // 4):
                        line = f"</li>\n<li>{line[line.index('- ') + 2:]}"
                    elif current_level < (len(line[:line.index(line[:line_pattern.match(line).end()].strip())]) // 4):
                        line = f"<ul><li>{line[line.index('- ') + 2:]}"
                        current_level += 1
                        lists.append("ul")
                    else:
                        temp_line = ""
                        while current_level > (
                                len(line[:line.index(line[:line_pattern.match(line).end()].strip())]) // 4):
                            temp_line += f"</li>\n</{lists[-1]}>"
                            current_level -= 1
                            lists.pop()
                        line = f"{temp_line}</li>\n<li>{line[line.index('- ') + 2:]}"
            elif (len(line) == 0 or (len(line) > 0 and not (
                    numeric_list_pattern.match(line.strip()) and points_list_pattern.match(
                line.strip())))) and current_level > -1:
                result.append(f"</li>\n</{lists[-1]}>")
                current_level -= 1
                lists.pop()
            result.append(line)

            if i + 1 == len(lines) and current_level > -1:
                while current_level > -1:
                    result.append(f"</li>\n</{lists[-1]}>")
                    current_level -= 1

        return "\n".join(result)

    def parse_code_block(self, text: str, parsing_info: ParsingInfo) -> str:
        if (parsing_info.i - 1 < 0 or text[parsing_info.i - 1] == " " or text[parsing_info.i - 1] == "\n") and text[parsing_info.i + 1] != "`":
            j = text[parsing_info.i + 1:].find("`") + (parsing_info.i + 1)
            if text[j + 1] != "`":
                replacement = f"<span class='code'>{text[parsing_info.i + 1:j]}</span>"
                if parsing_info.i == 0:
                    text = replacement + text[j + 1:]
                else:
                    text = text[:parsing_info.i] + replacement + text[j + 1:]
                parsing_info.i += (len(replacement) - 2)
            else:
                parsing_info.i += 1
        elif (parsing_info.i - 1 < 0 or text[parsing_info.i - 1] == "\n") and text[parsing_info.i + 1] == "`" and text[parsing_info.i + 2] == "`":
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
            parsing_info.i += 1

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

    def parse_image(self, text: str) -> str:
        return re.sub(r"!\[(.*)]\((.*)\)", "<img src='\g<2>' alt='\g<1>' />", text)

    def parse_italic_bold(self, text: str) -> str:
        strikethrough = re.sub(r"(~~)(.*)(~~)", "<span class='strikethrough'>\g<2></span>", text)
        bi = re.sub(r"(\*\*\*)(.*)(\*\*\*)", "<strong><em>\g<2></em></strong>", strikethrough)
        b = re.sub(r"(\*\*)(.*)(\*\*)", "<strong>\g<2></strong>", bi)
        return re.sub(r"(\*)(.*)(\*)", "<em>\g<2></em>", b)

    def parse_escaped_characters(self, text: str) -> str:
        return text
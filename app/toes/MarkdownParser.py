import re


class MarkdownParser:
    def __init__(self, *args, path, **kwargs):
        with open(path, mode="r") as text_file:
            self.text = text_file.read()

    def to_html_string(self) -> str:
        result = self.parse_paragraphs(self.text)
        result = self.parse_headlines(result)
        result = self.parse_image(result)
        result = self.parse_link(result)
        result = self.parse_footnotes(result)

        return result

    def parse_paragraphs(self, text: str) -> str:
        lines = text.split("\n")
        result = []
        paragraph_start_pattern = re.compile('(\d+)? ?[a-zA-z]+')
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

    def parse_list(self, text: str) -> str:
        lines = text.split("\n")
        result = []
        paragraph_start_pattern = re.compile('(\d+\. )|(* )')
        for line in lines:
            if len(line) > 0 and paragraph_start_pattern.match(line):
                line = f"<p>{line}</p>"
            result.append(line)

        return "\n".join(result)

    def parse_code_block(self, text: str) -> str:
        pass

    def parse_footnotes(self, text: str) -> str:
        # \[\d+\. .+?\]
        footnote_pattern = r"\[\d+\. .+?\]"
        re_fp = re.compile(footnote_pattern)
        footnotes = re_fp.findall(text)
        list = "<ul>"
        for note in footnotes:
            index = note[1:note.find(".")]
            text = text.replace(note, f"<sup><a href='#footnote-{index}' id='footnote-link-{index}'>{index}.</a></sup>")

            list += f"<li id='footnote-{index}'>{note[note.find('. ') + 2:len(note)-1]}"
            list += f"<a href='#footnote-link-{index}'>🔼</a></li>"

        list += "</ul>"
        if len(footnotes) > 0:
            return " ".join([text, list])
        return text

    def parse_link(self, text: str) -> str:
        return re.sub(r"([^!]|^)\[(.*)]\((.*)\)", "\g<1><a href='\g<3>'>\g<2></a>", text)

    def parse_image(self, text: str) -> str:
        return re.sub(r"!\[(.*)]\((.*)\)", "<img src='\g<2>' alt='\g<1>' />", text)
        # [!]\[(.*)]\((.*)\)

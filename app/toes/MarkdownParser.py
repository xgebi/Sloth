import re


class MarkdownParser:
    def __init__(self, *args, path, **kwargs):
        with open(path, mode="r") as text_file:
            self.text = text_file.read()

    def to_html_string(self) -> str:
        result = self.parse_paragraphs(self.text)
        result = self.parse_headlines(result)

        return result

    def parse_paragraphs(self, text: str) -> str:
        lines = text.split("\n")
        result = []
        paragraph_start_pattern = re.compile('(\d+)? ?[a-zA-z]+')
        for line in lines:
            if len(line) > 0 and paragraph_start_pattern.match(line):
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
                line = f"<h{level}>{line}</h{level}>"
            result.append(line)
        return "\n".join(result)

    def parse_list(self, text: str) -> str:
        pass

    def parse_code(self, text: str) -> str:
        pass

    def parse_footnotes(self, text: str) -> str:
        pass

    def parse_link(self, text: str) -> str:
        pass

    def parse_image(self, text: str) -> str:
        pass

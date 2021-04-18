from typing import Dict

from app.toes.text_node import TextNode


class CommentNode(TextNode):
    def to_html_string(self) -> str:
        return f"<!-- {self.text} -->"

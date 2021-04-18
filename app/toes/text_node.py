from typing import Dict, List
from app.toes.node import Node


class TextNode(Node):
    def __init__(
            self,
            *args,
            parent: 'Node' = None,
            cdata: bool = False,
            content: str = "",
            **kwargs
    ) -> None:
        super(TextNode, self).__init__(
            parent=parent,
            paired_tag=False,
            children=None,
            attributes=None
        )
        self.text = True
        self.cdata = cdata
        self.content = content
        self.type = Node.CDATA_TEXT if cdata else Node.TEXT

    def to_html_string(self) -> str:
        return self.content

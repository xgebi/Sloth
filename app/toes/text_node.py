from typing import Dict, List
from app.toes.node import Node


class TextNode(Node):
    def __init__(
            self,
            *args,
            parent: 'Node' = None,
            cdata: bool = False,
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
        self.content = ""

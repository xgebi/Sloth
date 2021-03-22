from typing import Dict

from app.toes.node import Node


class ProcessingNode(Node):
    def __init__(self, parent: Node, name: str = "", attributes: Dict = {}):
        super(ProcessingNode, self).__init__(
            name=name,
            parent=parent,
            paired_tag=False,
            attributes=attributes
        )
        self.type = Node.PROCESSING

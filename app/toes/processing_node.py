from app.toes.node import Node


class ProcessingNode(Node):
    def __init__(self, parent: Node):
        super(ProcessingNode, self).__init__(
            parent=parent,
            paired_tag=False,
            children=None,
            attributes=[]
        )

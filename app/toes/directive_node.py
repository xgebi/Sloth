from app.toes.node import Node


class DirectiveNode(Node):
    def __init__(self, parent: Node):
        super(DirectiveNode, self).__init__(
            parent=parent,
            paired_tag=False,
            children=None,
            attributes=[]
        )

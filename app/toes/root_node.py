from app.toes.node import Node


class RootNode(Node):
    def __init__(
            self
    ) -> None:
        super().__init__(name='xml',
                         attributes={},
                         children=[],
                         paired_tag=False)
        self.special_tag = True
        self.parent = None
        self.children = []

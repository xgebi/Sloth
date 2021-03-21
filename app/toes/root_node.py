from typing import List, Dict

from app.toes.processing_node import ProcessingNode


class RootNode(ProcessingNode):

    def __init__(self):
        super(RootNode, self).__init__(
            name="xml",
            parent=None,
            attributes={
                "encoding": "utf-8",
                "xml_version": "1.0"
            }
        )

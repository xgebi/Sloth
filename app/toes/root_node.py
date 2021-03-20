from typing import List, Dict

from app.toes.node import Node


class RootNode:

    def __init__(self):
        self.type = ""
        self.attributes = {
            "encoding": "utf-8",
            "xml_version": "1.0"
        }
        self.children: List[Node] = []

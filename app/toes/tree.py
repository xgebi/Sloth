from typing import List, Dict

from app.toes.node import Node


class Tree:

    def __init__(self):
        self.type = ""
        self.attributes = {
            "encoding": "utf-8",
            "xml_version": "1.0"
        }
        self.directives: List[Node] = []
        self.children: List[Node] = []

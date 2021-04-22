from typing import List


class Hook:
    def __init__(self,
                 content: str,
                 condition: str
                 ) -> None:
        self.content = content
        self.condition = condition


class Hooks:
    def __init__(self) -> None:
        self.footer: List[Hook] = []
        self.head: List[Hook] = []

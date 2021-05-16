from typing import List
import enum


class Hook:
    def __init__(self,
                 content: str,
                 condition: str
                 ) -> None:
        self.content = content
        self.condition = condition


class HooksList(enum.Enum):
    footer = 'footer'
    head = 'head'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, HooksList))


class Hooks:
    def __init__(self) -> None:
        self.footer: List[Hook] = []
        self.head: List[Hook] = []

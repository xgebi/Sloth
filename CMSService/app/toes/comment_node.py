from typing import Dict

from app.toes.text_node import TextNode


class CommentNode(TextNode):
	def __init__(
			self,
			*args,
			parent: 'Node' = None,
			cdata: bool = False,
			content: str = "",
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
		self.content = content
		self.type = TextNode.COMMENT

	def to_html_string(self) -> str:
		return f"<!-- {self.content} -->\n"

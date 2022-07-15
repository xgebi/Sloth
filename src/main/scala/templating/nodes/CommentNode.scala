package templating.nodes

class CommentNode(cdata: Boolean = false, content: String, parent: Node) extends Node (name="", null, parent = parent, nodeType = Node.COMMENT) {
  override def toHTMLString: String = s"<!-- $content -->\n"
}
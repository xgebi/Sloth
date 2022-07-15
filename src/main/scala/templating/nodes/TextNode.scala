package templating.nodes

class TextNode(cdata: Boolean = false, content: String, parent: Node) extends Node (name="", null, parent = parent, nodeType = Node.TEXT) {
  override def toHTMLString: String = s"$content\n"
}

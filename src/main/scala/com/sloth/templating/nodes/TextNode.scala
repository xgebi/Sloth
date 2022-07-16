package com.sloth.templating.nodes

class TextNode(cdata: Boolean = false, content: String, parent: Node) extends Node (name="", null, parent = parent, nodeType = Node.TEXT) {
  override def toHTMLString: String = {
    if (cdata) {
      s"<![CDATA[$content]]>"
    } else {
      s"$content"
    }
  }
}

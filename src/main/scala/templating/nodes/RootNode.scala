package templating.nodes

import scala.collection.mutable.ListBuffer

class RootNode(val html: Boolean = false, doctype: String = "") extends Node("xml", ListBuffer(), false, Node.ROOT) {
  if (html) {
    super.setAttribute("doctype", if (doctype.nonEmpty)  doctype else "html")
  } else {
    super.setAttribute("encoding", "utf-8")
    super.setAttribute("xml_version", "1.0")
  }


  override def toHTMLString: String = {
    val formattedAttributes = super.attributesAsString

    val childrenAsList: ListBuffer[String] = new ListBuffer()
    this.children foreach {case (child: Node) => childrenAsList.addOne(child.toHTMLString) }
    s"<!DOCTYPE $formattedAttributes>${childrenAsList.mkString("\n")}"
  }
}
package com.sloth.templating.nodes

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

class DirectiveNode(name: String = "", children: ListBuffer[Node] = ListBuffer(), parent: Node, attributes: mutable.HashMap[String, String] = mutable.HashMap() )
  extends Node(name = name, children = children, argPairedTag = false, nodeType = Node.DIRECTIVE, parent = parent, attributes = attributes) {

}

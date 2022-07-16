package com.sloth.templating.nodes

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

class DirectiveNode(name: String = "", children: ListBuffer[Node], parent: Node, attributes: mutable.HashMap[String, String] )
  extends Node(name = name, children = children, argPairedTag = false, nodeType = Node.DIRECTIVE, parent = parent, attributes = attributes) {

}

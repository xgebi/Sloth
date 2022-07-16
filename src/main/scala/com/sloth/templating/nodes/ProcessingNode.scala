package com.sloth.templating.nodes

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

class ProcessingNode(name: String = "", children: ListBuffer[Node] = ListBuffer(), parent: Node, attributes: mutable.HashMap[String, String] = mutable.HashMap())
  extends Node(name = name, children = children, argPairedTag = false, nodeType = Node.PROCESSING, parent = parent, attributes = attributes) {

}

package com.sloth.templating.nodes

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

class ProcessingNode(name: String = "", children: ListBuffer[Node], parent: Node, attributes: mutable.HashMap[String, String] )
  extends Node(name = name, children = children, argPairedTag = false, nodeType = Node.PROCESSING, parent = parent, attributes = attributes) {

}

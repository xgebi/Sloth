package com.sloth.templating.nodes

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

object Node {
  val NODE = "node"
	val ROOT = "root"
	val PROCESSING = "processing"
	val DIRECTIVE = "directive"
	val TEXT = "text"
	val COMMENT = "comment"
	val CDATA_TEXT = "cdata"

	val UNPAIRED_TAGS: List[String] = List("base", "br", "meta", "hr", "img", "track", "source", "embed", "col", "input", "link")
	val ALWAYS_PAIRED: List[String] = List("script")
}

class Node(
						val name: String,
						val children: ListBuffer[Node],
						argPairedTag: Boolean = true,
						nodeType: String = Node.NODE,
						val parent: Node = null,
						attributes: mutable.HashMap[String, String] = mutable.HashMap()) {
	val pairedTag: Boolean = {
		if (Node.UNPAIRED_TAGS.contains(name)) {
			false
		} else if (Node.ALWAYS_PAIRED.contains(name)) {
			true
		} else {
			argPairedTag
		}
	}

	def setName(name: String): Node = {
		new Node(name = name, children = this.children, argPairedTag = this.pairedTag, nodeType = this.nodeType, parent = this.parent, attributes = this.attributes)
	}

	def addChild(child: Node): Node = {
		if (this.pairedTag) {
			children.addOne(child)
		}
		child
	}

	def replaceChild(replacee: Node, replacer: Node): Unit = {
		val replaceeIndex = this.children.indexOf(replacee);
		this.children.remove(replaceeIndex, 1);
		this.children.insert(replaceeIndex, replacer)
	}

	def removeChild(toBeRemoved: Node): Node = {
		val removeIndex = this.children.indexOf(toBeRemoved);
		this.children.remove(removeIndex, 1);
		toBeRemoved
	}

	def setAttribute(name: String, value: String): Unit = {
		if (this.hasAttribute(name)) {
			this.attributes.update(name, value)
		} else {
			this.attributes.addOne(name, value)
		}
	}

	def getAttribute(name: String): Option[String] = {
		this.attributes.get(name)
	}

	def hasAttribute(name: String): Boolean = {
		this.getAttribute(name) match {
			case Some(_) => true
			case None => false
		}
	}

	def removeAttribute(name: String): Unit = {
		this.attributes.remove(name)
	}

	def attributesAsString: String = {
		val attributeListFormatted: ListBuffer[String] = new ListBuffer()
		this.attributes foreach {case (key, value) => { attributeListFormatted.addOne(f"${key}='${value}'") } }
		attributeListFormatted.mkString(" ")
	}

	def toHTMLString: String = {
		val formattedAttributes = this.attributesAsString

		if (this.pairedTag) {
			val childrenAsList: ListBuffer[String] = new ListBuffer()
			this.children foreach {case (child: Node) => childrenAsList.addOne(child.toHTMLString) }
			s"<${this.name} $formattedAttributes>${childrenAsList.mkString("\n")}</${this.name}>"
		} else {
			s"<${this.name} $formattedAttributes />"
		}
	}
}

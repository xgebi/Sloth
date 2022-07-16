package com.sloth.templating.nodes

import org.scalatest.funsuite.AnyFunSuite

import scala.collection.mutable.ListBuffer

class CommentNodeTests extends AnyFunSuite {
  // comment node was created
  test("Comment node is created") {
    val n = new CommentNode(content = "This is a comment node", parent = null)
    assert(n != null)
  }
  // to html string
  test("Comment node to html string") {
    val n = new CommentNode(content = "This is a comment node", parent = null)
    assert(n != null)
    assert(n.toHTMLString == "<!-- This is a comment node -->\n")
  }
}

package com.sloth.templating.nodes

import org.scalatest.funsuite.AnyFunSuite

class TextNodeTests extends AnyFunSuite {
  test("Text node is created") {
    val n = new TextNode(content = "This is a text node", parent = null)
    assert(n != null)
  }
  test("Text node to html string, no CDATA") {
    val n = new TextNode(content = "This is a text node", parent = null)
    assert(n != null)
    assert(n.toHTMLString == "This is a text node")
  }

  test("Text node to html string with CDATA") {
    val n = new TextNode(content = "This is a text node", parent = null, cdata = true)
    assert(n != null)
    assert(n.toHTMLString == "<![CDATA[This is a text node]]>")
  }
}


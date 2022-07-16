package com.sloth.templating.XMLParser

import com.sloth.templating.exceptions.XMLParsingException
import org.scalatest.funsuite.AnyFunSuite
import com.sloth.templating.nodes.{Node, TextNode}

class XMLParserTests extends AnyFunSuite{
  test("XMLParser was created") {
    val xp = new XMLParser("test template")
    assert(xp != null)
  }

  test("read node name") {
    val xp = new XMLParser("test template")
    assert(xp != null)
  }

  test("look for attribute - ! moves index") {
    val xp = new XMLParser("!my-attr='abc'>test template")
    assert(xp != null)
    xp.lookForAttribute()
    assert(xp.parsingInfo.idx == 1)
  }

  test("look for attribute - throws exception because tag is not finished") {
    val xp = new XMLParser("test template")
    assert(xp != null)
    assertThrows[XMLParsingException] {
      xp.lookForAttribute()
    }
  }

  test("look for attribute - parses attribut without value") {
    val xp = new XMLParser("my-attr>test template")
    assert(xp != null)
    xp.parsingInfo.currentNode = new Node(name = "a")
    xp.lookForAttribute()
    assert(xp.parsingInfo.idx == 7)
    assert(xp.parsingInfo.currentNode.getAttribute("my-attr").get == "")
  }

  test("look for attribute - parses attribute with value") {
    val xp = new XMLParser("my-attr='abc'>test template")
    assert(xp != null)
    xp.parsingInfo.currentNode = new Node(name = "a")
    xp.lookForAttribute()
    assert(xp.parsingInfo.idx == 14)
    assert(xp.parsingInfo.currentNode.getAttribute("my-attr").get == "abc")
  }

  test("look for child nodes") {
    val xp = new XMLParser("<a>test template</a>")
    assert(xp != null)
    xp.parsingInfo.currentNode = new Node(name = "a")
    xp.parsingInfo.moveIndex(3)
    xp.lookingForChildTextNodes()
    assert(xp.parsingInfo.currentNode.children.length == 1)
    assert(xp.parsingInfo.currentNode.children.head.asInstanceOf[TextNode].toHTMLString == "test template")
  }

  test("look for child nodes should throw exception") {
    val xp = new XMLParser("<a>test template")
    assert(xp != null)
    xp.parsingInfo.currentNode = new Node(name = "a")
    xp.parsingInfo.moveIndex(3)
    assertThrows[XMLParsingException] {
      xp.lookingForChildTextNodes()
    }
  }
}

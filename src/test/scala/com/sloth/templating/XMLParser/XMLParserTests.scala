package com.sloth.templating.XMLParser

import com.sloth.templating.exceptions.XMLParsingException
import com.sloth.templating.nodes.{Node, TextNode}
import org.scalatest.funspec.AnyFunSpec

class XMLParserTests extends AnyFunSpec  {
  it("XMLParser was created") {
    val xp = new XMLParser("test template")
    assert(xp != null)
  }

  describe("parse starting tag character") {
    it("parse starting tag character") {
      val xp = new XMLParser("a>test template")
      assert(xp != null)
    }
  }

  describe("parse ending tag character") {
    it("parse ending tag character") {
      val xp = new XMLParser("a>test template")
      assert(xp != null)
    }
  }

  describe("read node name") {
    it("read node name - >") {
      val xp = new XMLParser("a>test template")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node("")
      xp.readNodeName()
      assert(xp.parsingInfo.currentNode.name == "a")
    }

    it("read node name - [ ]") {
      val xp = new XMLParser("a >test template")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node("")
      xp.readNodeName()
      assert(xp.parsingInfo.currentNode.name == "a")
    }

    it("read node name - />") {
      val xp = new XMLParser("a/>test template")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node("")
      xp.readNodeName()
      assert(xp.parsingInfo.currentNode.name == "a")
    }

    it("read node name - \n") {
      val xp = new XMLParser("a\n>test template")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node("")
      xp.readNodeName()
      assert(xp.parsingInfo.currentNode.name == "a")
    }
  }

  describe("look for attribute") {
    it("look for attribute - ! moves index") {
      val xp = new XMLParser("!my-attr='abc'>test template")
      assert(xp != null)
      xp.lookForAttribute()
      assert(xp.parsingInfo.idx == 1)
    }

    it("look for attribute - throws exception because tag is not finished") {
      val xp = new XMLParser("test template")
      assert(xp != null)
      assertThrows[XMLParsingException] {
        xp.lookForAttribute()
      }
    }

    it("look for attribute - throws exception because attribute value not in quotes") {
      val xp = new XMLParser("my-attr=abc>test template")
      assert(xp != null)
      assertThrows[XMLParsingException] {
        xp.lookForAttribute()
      }
    }

    it("look for attribute - throws exception because unpaired quotes") {
      val xp = new XMLParser("my-attr=\"abc>test template")
      assert(xp != null)
      assertThrows[XMLParsingException] {
        xp.lookForAttribute()
      }
    }

    it("look for attribute - parses attribut without value") {
      val xp = new XMLParser("my-attr>test template")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node(name = "a")
      xp.lookForAttribute()
      assert(xp.parsingInfo.idx == 7)
      assert(xp.parsingInfo.currentNode.getAttribute("my-attr").get == "")
    }

    it("look for attribute - parses attribute with value") {
      val xp = new XMLParser("my-attr='abc'>test template")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node(name = "a")
      xp.lookForAttribute()
      assert(xp.parsingInfo.idx == 14)
      assert(xp.parsingInfo.currentNode.getAttribute("my-attr").get == "abc")
    }
  }

  describe("look for child nodes") {
    it("look for child nodes succeeds") {
      val xp = new XMLParser("<a>test template</a>")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node(name = "a")
      xp.parsingInfo.moveIndex(3)
      xp.lookingForChildTextNodes()
      assert(xp.parsingInfo.currentNode.children.length == 1)
      assert(xp.parsingInfo.currentNode.children.head.asInstanceOf[TextNode].toHTMLString == "test template")
    }

    it("look for child nodes should throw exception") {
      val xp = new XMLParser("<a>test template")
      assert(xp != null)
      xp.parsingInfo.currentNode = new Node(name = "a")
      xp.parsingInfo.moveIndex(3)
      assertThrows[XMLParsingException] {
        xp.lookingForChildTextNodes()
      }
    }
  }
}

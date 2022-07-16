package com.sloth.templating.nodes

import org.scalatest.funspec.AnyFunSpec

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

class NodeTests extends AnyFunSpec {
  it("Node is created") {
    val n = new Node("", ListBuffer())
    assert(n != null)
  }

  describe("is tag paired") {
    it("script is always paired") {
      val n = new Node("script", argPairedTag = false)
      assert(n != null)
      assert(n.isPairedTag)
    }

    it("br is not paired") {
      val n = new Node("br", argPairedTag = false)
      assert(n != null)
      assert(!n.isPairedTag)
    }

    it("div is not paired") {
      val n = new Node("div", argPairedTag = false)
      assert(n != null)
      assert(!n.isPairedTag)
    }

    it("div is paired") {
      val n = new Node("div", argPairedTag = true)
      assert(n != null)
      assert(n.isPairedTag)
    }
  }

  it("set name to node") {
    val n = new Node("")
    assert(n != null)
    val n1 = n.setName("br")
    assert(n1 != null)
    assert(n1.name == "br")
  }

  describe("Adding children") {
    it("fail to add child to unpaired tag") {
      val n = new Node("br")
      assert(n != null)
      val child = new Node("div")
      assert(child != null)
      n.addChild(child)
      assert(n.children.knownSize == 0)
    }

    it("adds child to paired tag") {
      val n = new Node("section")
      assert(n != null)
      val child = new Node("div")
      assert(child != null)
      n.addChild(child)
      assert(n.children.knownSize == 1)
    }
  }

  it("removes a child") {
    val n = new Node("section")
    assert(n != null)
    val child = new Node("div")
    assert(child != null)
    n.addChild(child)
    assert(n.children.knownSize == 1)
    n.removeChild(child)
    assert(n.children.knownSize == 0)
  }

  it("get attribute") {
    val n = new Node("", attributes = mutable.HashMap("abc" -> "test"))
    assert(n != null)
    assert(n.getAttribute("abc").get == "test")
  }

  describe("setting an attribute") {
    it("set new attribute") {
      val n = new Node("")
      assert(n != null)
      n.setAttribute("abc", "test")
      assert(n.getAttribute("abc").get == "test")
    }

    it("set existing attribute") {
      val n = new Node("", attributes = mutable.HashMap("abc" -> "test"))
      assert(n != null)
      n.setAttribute("abc", "test2")
      assert(n.getAttribute("abc").get == "test2")
    }
  }

  describe("removing an attribute") {
    it("remove existing attribute") {
      val n = new Node("", attributes = mutable.HashMap("abc" -> "test"))
      assert(n != null)
      n.removeAttribute("abc")
      assert(n.getAttribute("abc").isEmpty)
    }

    it("remove non-existing attribute") {
      val n = new Node("")
      assert(n != null)
      n.removeAttribute("abc")
      assert(n.getAttribute("abc").isEmpty)
    }
  }

  it("attributes as string") {
    val n = new Node("", attributes = mutable.HashMap("abc" -> "test"))
    assert(n != null)
    assert(n.attributesAsString == "abc='test'")
  }

  describe("tag to html string") {
    it("to html string - unpaired tag") {
      val n = new Node("br")
      assert(n != null)
      assert(n.toHTMLString == "<br />")
    }

    it("to html string - paired tag") {
      val n = new Node("div")
      assert(n != null)
      assert(n.toHTMLString == "<div></div>")
    }

    it("to html string - unpaired tag with attributes") {
      val n = new Node("br", attributes = mutable.HashMap("class" -> "test"))
      assert(n != null)
      assert(n.toHTMLString == "<br class='test' />")
    }

    it("to html string - paired tag with attributes") {
      val n = new Node("div", attributes = mutable.HashMap("class" -> "test"))
      assert(n != null)
      assert(n.toHTMLString == "<div class='test'></div>")
    }

    it("to html string - paired tag with attributes and child") {
      val child = new Node("div")
      val n = new Node("div", attributes = mutable.HashMap("class" -> "test"), children = ListBuffer(child))
      assert(n != null)
      assert(n.toHTMLString == "<div class='test'><div></div></div>")
    }
  }
}

package com.sloth.templating.nodes

import org.scalatest.funsuite.AnyFunSuite

import scala.collection.mutable.ListBuffer

class NodeTests extends AnyFunSuite{
  test("Node is created") {
    val n = new Node("", ListBuffer())
    assert(n != null)
  }

  test("script is always paired") {
    val n = new Node("script", ListBuffer(), false)
    assert(n != null)
    assert(n.isPairedTag)
  }

  test("br is not paired") {
    val n = new Node("br", ListBuffer(), false)
    assert(n != null)
    assert(!n.isPairedTag)
  }

  test("set name to node") {
    val n = new Node("", ListBuffer())
    assert(n != null)
    val n1 = n.setName("br")
    assert(n1 != null)
    assert(n1.name == "br")
  }
  // add child
  // replace child
  // remove child
  // set attribute
  // get attribute
  // remove attribute
  // attributes as string
  // to html string
}

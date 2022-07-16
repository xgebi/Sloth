package com.sloth.templating.XMLParser

import org.scalatest.funsuite.AnyFunSuite

class XMLParsingInfoTests extends AnyFunSuite{
  test("XMLParsingInfo was created") {
    val xpi = new XMLParsingInfo()
    assert(xpi.idx == 0)
  }

  test("Default move index") {
    val xpi = new XMLParsingInfo()
    xpi.moveIndex()
    assert(xpi.idx == 1)
  }

  test("Move index by 2") {
    val xpi = new XMLParsingInfo()
    xpi.moveIndex(2)
    assert(xpi.idx == 2)
  }

  test("Move index by 2 twice") {
    val xpi = new XMLParsingInfo()
    xpi.moveIndex(2)
    xpi.moveIndex(2)
    assert(xpi.idx == 4)
  }

  test("Move index by -1") {
    val xpi = new XMLParsingInfo()
    xpi.moveIndex(-1)
    assert(xpi.idx == 0)
  }

  test("Add to result") {
    val xpi = new XMLParsingInfo()
    xpi.addToResult("abc")
    assert(xpi.result == "abc")
    assert(xpi.idx == 3)
  }
}

package com.sloth.templating.XMLParser

import org.scalatest.funsuite.AnyFunSuite

class XMLParserTests extends AnyFunSuite{
  test("XMLParser was created") {
    val xp = new XMLParser("test template")
    assert(xp != null)
  }
}

package com.sloth.templating.XMLParser

import com.sloth.templating.nodes._

class XMLParsingInfo(var idx: Int = 0, var state: Int = ParsingStates.NEW_PAGE, var currentNode: Node = null, var rootNode: Node = null) {
  def moveIndex(step: Int = 1): Unit = {
    if (step > 0) {
      this.idx += step
    }
  }
}

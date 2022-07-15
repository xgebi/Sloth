package templating.XMLParser

import templating.nodes._

class XMLParsingInfo(var idx: Int = 0, var state: Int = ParsingStates.NEW_PAGE, var currentNode: Node, rootNode: Node) {
  def moveIndex(step: Int = 1): Unit = {
    this.idx += step
  }
}

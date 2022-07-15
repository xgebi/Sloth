package templating.XMLParser

object ParsingStates {
  val NEW_PAGE = 0
	val READ_NODE_NAME = 1
	val LOOKING_FOR_ATTRIBUTE = 2
	val LOOKING_FOR_CHILD_NODES = 3
	val INSIDE_SCRIPT = 4
}

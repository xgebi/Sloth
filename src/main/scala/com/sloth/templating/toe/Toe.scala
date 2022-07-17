package com.sloth.templating.toe

import com.sloth.templating.nodes._

class Toe {
  def processTree(): Unit = {

  }

  def processSubtree(newTreeParent: Node, templateTreeNode: Node): Node = {
    null
  }

  def processConditionalCssClasses(newTreeNode: Node, conditionAttr: String): Unit = {

  }

  def processCssClassCondition(condition: String): String = {
    null
  }

  def processConditionalAttributes(newTreeNode: Node, conditionAttr: String, attrName: String): Unit = {

  }

  def processInlineJS(newTree: Node, nodes: List[TextNode]): Unit = {

  }

  def processToeTag(parentElement: Node, element: Node): Unit = {

  }

  def processHeadHooks(parentNode: Node): Unit = {

  }

  def processFooterHooks(parentNode: Node): Unit = {

  }

  def processToeImportTag(generatedTree: Node, element: Node): Unit = {

  }

  def processToeValue(attributeValue: String): String = {
    null
  }

  def processAssignTag(element: Node): Unit = {

  }

  def processCreateTag(element: Node): Unit = {

  }

  def processModifyTag(element: Node): Unit = {

  }

  def processIfAttribute(parentElement: Node, element: Node): Node = {
    null
  }

  def processForAttribute(parentElement: Node, element: Node): Node = {
    null
  }

  def processWhileAttribute(parentElement: Node, element: Node): Node = {
    null
  }

  def processPipe(side: String): String = {
    null
  }
}

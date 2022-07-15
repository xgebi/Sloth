package templating.XMLParser

import templating.exceptions.{EmptyTemplateException, XMLParsingException}
import templating.nodes._
import utilities.Utilities

import scala.collection.mutable.ListBuffer
import scala.util.control.Breaks.break

/**
 * Class responsible for parsing XML into Node tree
 *
 * @param template A template to be parsed
 */
class XMLParser(template: String) {
  val parsingInfo = new XMLParsingInfo()

  /**
   * Main function to be interacted with. Parses template into nodes.
   *
   * @return A new containing root node of the tree
   */
  def parse: Node = {
    if (this.template.isEmpty) {
      throw new EmptyTemplateException("template cannot be empty")
    }

    while (parsingInfo.idx < this.template.length) {
      this.template.charAt(parsingInfo.idx).toString match {
        case "<" => ??? // result, parsing_info = self.parse_starting_tag_character(text=result, parsing_info=parsing_info)
        case ">" => ??? // result, parsing_info = self.parse_ending_tag_character(text=result, parsing_info=parsing_info)
        case " " | "\n" | "\t" => parsingInfo.moveIndex()
        case _ => this.parseCharacter
      }
    }

    new Node(name = "abc", children = ListBuffer(), argPairedTag = true)
  }

  /**
   * Function which decides what to do when a character is encountered
   */
  def parseCharacter(): Unit = {
    parsingInfo.state match {
      case ParsingStates.READ_NODE_NAME => this.readNodeName()
      case ParsingStates.LOOKING_FOR_ATTRIBUTE =>
    }
  }

  /**
   * Reads a name of the element and moves parser further
   */
  def readNodeName(): Unit = {
    val nameEnd = Utilities.positiveMinInt(List(
      this.template.substring(parsingInfo.idx).indexOf(" "),
      this.template.substring(parsingInfo.idx).indexOf(">"),
      this.template.substring(parsingInfo.idx).indexOf("/>"),
      this.template.substring(parsingInfo.idx).indexOf("\n")
    )) + parsingInfo.idx
    parsingInfo.currentNode.setName(this.template.substring(parsingInfo.idx, nameEnd))
    parsingInfo.moveIndex(this.template.substring(parsingInfo.idx, nameEnd).length)
    parsingInfo.state = ParsingStates.LOOKING_FOR_ATTRIBUTE
  }

  /**
   * Function dealing with attributes in current node
   */
  def lookForAttribute(): Unit = {
    if (this.template.charAt(parsingInfo.idx).isLetterOrDigit) {
      val attrDivider = this.template.substring(parsingInfo.idx).indexOf("=")
      val tagEnd = this.template.substring(parsingInfo.idx).indexOf(">")

      if (tagEnd == -1) {
        throw new XMLParsingException("Not properly closed tag")
      }
      if (attrDivider > tagEnd || attrDivider < 0) {
        val attrName = this.template.substring(parsingInfo.idx, parsingInfo.idx + Utilities.positiveMinInt(List(
          this.template.substring(parsingInfo.idx).indexOf(" "),
          this.template.substring(parsingInfo.idx).indexOf(">"),
          this.template.substring(parsingInfo.idx).indexOf("/>"),
        )))
        val attrValue = ""
        parsingInfo.moveIndex(attrName.length)
      } else {
        val equalsPosition = parsingInfo.idx + this.template.substring(parsingInfo.idx).indexOf("=")
        val attrName = this.template.substring(parsingInfo.idx, equalsPosition)
        val attrValQuoteChar = this.template.charAt(parsingInfo.idx + this.template.substring(parsingInfo.idx).indexOf("=") + 1)
        if (attrValQuoteChar.toString != "\"" && attrValQuoteChar.toString != "'") {
          throw new XMLParsingException("Attribute is not in quotes")
        }
        var attrValEndCharPosition: Int = parsingInfo.idx + this.template.substring(parsingInfo.idx).indexOf("=") + 2
        val attrValue: String = {
          var result = ""
          while (attrValEndCharPosition < this.template.length) {
            if (this.template.charAt(attrValEndCharPosition) == attrValQuoteChar && this.template.charAt(attrValEndCharPosition - 1).toString != "\\") {
              result = this.template.substring(equalsPosition + 2, attrValEndCharPosition)
              break
            }
            attrValEndCharPosition += 1
          }
          result
        }
        parsingInfo.currentNode.setAttribute(attrName, attrValue)
        parsingInfo.moveIndex(f"$attrName='$attrValue'".length)
      }
    } else {
      parsingInfo.moveIndex()
    }
  }
}

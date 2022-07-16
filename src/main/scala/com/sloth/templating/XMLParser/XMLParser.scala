package com.sloth.templating.XMLParser

import com.sloth.templating.exceptions.{EmptyTemplateException, XMLParsingException}
import com.sloth.templating.nodes._
import com.sloth.utilities.Utilities

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
        case "<" => this.parseStartingTagCharacter() // result, parsing_info = self.parse_starting_tag_character(text=result, parsing_info=parsing_info)
        case ">" => this.parseEndingTagCharacter() // result, parsing_info = self.parse_ending_tag_character(text=result, parsing_info=parsing_info)
        case " " | "\n" | "\t" => parsingInfo.moveIndex()
        case _ => this.parseCharacter()
      }
    }

    new Node(name = "abc", children = ListBuffer(), argPairedTag = true)
  }

  def parseStartingTagCharacter(): Unit = {
    if (this.template(this.parsingInfo.idx + 1) == ' ') {
      // TODO this this, just in case
      this.parsingInfo.moveIndex()
    } else if (this.parsingInfo.state == ParsingStates.NEW_PAGE) {
      this.startingCharOnNewPage()
    } else if (this.parsingInfo.state == ParsingStates.LOOKING_FOR_CHILD_NODES) {
      this.startingCharLookingForChildNodes()
    } else {
      this.parsingInfo.moveIndex()
    }
  }

  def startingCharOnNewPage(): Unit = {

    /*
    if text[parsing_info.i:].find("<?xml") == 0:
				parsing_info.move_index(len("<?xml"))
				parsing_info.state = STATES.looking_for_attribute
			elif text[parsing_info.i:].find("<!DOCTYPE") == 0:
				parsing_info.current_node.html = True
				parsing_info.current_node.attributes["doctype"] = text[len("<!DOCTYPE "):text.find(">")]
				parsing_info.state = STATES.looking_for_child_nodes
				parsing_info.move_index(text.find(">"))
			else:
				parsing_info = self.create_new_node(text, parsing_info)
				parsing_info.state = STATES.read_node_name
     */
  }

  def startingCharLookingForChildNodes(): Unit = {

    /*
    if text[parsing_info.i:].find("<![CDATA[") == 0:
				parsing_info.move_index(len("<![CDATA["))
				parsing_info.current_node.add_child(
					TextNode(
						parent=parsing_info.current_node,
						cdata=True,
						text=text[parsing_info.i: text[parsing_info.i:].find("]]>")]
					)
				)
				parsing_info.move_index(len(text[parsing_info.i:].find("]]>") + len("]]>")))
			elif text[parsing_info.i:].find("<!--") == 0:
				comment_end_raw = text[parsing_info.i:].find("-->")
				if comment_end_raw == -1:
					raise XMLParsingException("Not properly closed tag")
				comment_end = parsing_info.i + comment_end_raw
				parsing_info.current_node.add_child(CommentNode(content=text[parsing_info.i + 4: comment_end].strip()))
				parsing_info.move_index(len(f"{text[parsing_info.i: comment_end]}-->"))
			elif text[parsing_info.i + 1] == "/":
				name = text[parsing_info.i + 2: parsing_info.i + 2 + text[parsing_info.i + 2:].find(">")]
				if parsing_info.current_node.get_name() == name:
					parsing_info.current_node = parsing_info.current_node.parent
					parsing_info.move_index(len(f"</{name}>"))
				else:
					print(text)
					print(text[parsing_info.i:])
					raise XMLParsingException()
			else:
				parsing_info.state = STATES.read_node_name
				parsing_info = self.create_new_node(text=text, parsing_info=parsing_info)
     */
  }

  def parseEndingTagCharacter(): Unit = {

  }

  /**
   * Function which decides what to do when a character is encountered
   */
  def parseCharacter(): Unit = {
    parsingInfo.state match {
      case ParsingStates.READ_NODE_NAME => this.readNodeName()
      case ParsingStates.LOOKING_FOR_ATTRIBUTE => this.lookForAttribute()
      case ParsingStates.LOOKING_FOR_CHILD_NODES => this.lookingForChildTextNodes()
      case _ => this.parsingInfo.moveIndex()
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
    parsingInfo.currentNode = parsingInfo.currentNode.setName(this.template.substring(parsingInfo.idx, nameEnd))
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
        parsingInfo.currentNode.setAttribute(attrName, attrValue)
        parsingInfo.moveIndex(attrName.length)
      } else {
        val equalsPosition = parsingInfo.idx + this.template.substring(parsingInfo.idx).indexOf("=")
        val attrName = this.template.substring(parsingInfo.idx, equalsPosition)
        val attrValQuoteChar = this.template.charAt(parsingInfo.idx + this.template.substring(parsingInfo.idx).indexOf("=") + 1)
        if (attrValQuoteChar.toString != "\"" && attrValQuoteChar.toString != "'") {
          throw new XMLParsingException("Attribute is not in quotes")
        }
        var attrValEndCharPosition: Int = parsingInfo.idx + this.template.substring(parsingInfo.idx).indexOf("=") + 1
        val attrValue: String = {
          var result = ""
          var resultChanged = false
          do {
            attrValEndCharPosition += 1
            if (this.template.charAt(attrValEndCharPosition) == attrValQuoteChar && this.template.charAt(attrValEndCharPosition - 1).toString != "\\") {
              result = this.template.substring(equalsPosition + 2, attrValEndCharPosition)
              resultChanged = true
            }
          } while ((attrValEndCharPosition < this.template.length - 1) && !(this.template.charAt(attrValEndCharPosition) == attrValQuoteChar && this.template.charAt(attrValEndCharPosition - 1).toString != "\\"))
          if (!resultChanged) {
            throw new XMLParsingException("XML file has unpaired quotes")
          }
          result
        }
        parsingInfo.currentNode.setAttribute(attrName, attrValue)
        parsingInfo.moveIndex(f"$attrName='$attrValue'".length + 1)
      }
    } else {
      parsingInfo.moveIndex()
    }
  }

  def lookingForChildTextNodes(): Unit = {
    val textEndRaw = this.template.substring(parsingInfo.idx).indexOf("<")
    if (textEndRaw == -1) {
      throw new XMLParsingException("Not properly closed tag")
    }
    val textEnd = parsingInfo.idx + textEndRaw
    parsingInfo.currentNode.addChild(new TextNode(content = this.template.substring(parsingInfo.idx, textEnd), parent = parsingInfo.currentNode))
    parsingInfo.moveIndex(this.template.substring(parsingInfo.idx, textEnd).length)
  }
}

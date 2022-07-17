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
class XMLParser(template: String, rootNode: RootNode = new RootNode()) {
  val parsingInfo = new XMLParsingInfo(rootNode = rootNode, currentNode = rootNode)

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
        case "<" => this.parseStartingTagCharacter()
        case ">" => this.parseEndingTagCharacter()
        case " " | "\n" | "\t" => parsingInfo.moveIndex()
        case _ => this.parseCharacter()
      }
    }

    new Node(name = "abc", children = ListBuffer(), argPairedTag = true)
  }

  /**
   * This function is called when "<" is encountered
   */
  def parseStartingTagCharacter(): Unit = {
    if (this.template(this.parsingInfo.idx + 1) == ' ') {
      // TODO test this, just in case
      this.parsingInfo.moveIndex()
    } else if (this.parsingInfo.state == ParsingStates.NEW_PAGE) {
      this.startingCharOnNewPage()
    } else if (this.parsingInfo.state == ParsingStates.LOOKING_FOR_CHILD_NODES) {
      this.startingCharLookingForChildNodes()
    } else {
      this.parsingInfo.moveIndex()
    }
  }

  /**
   * Creates a new node
   *
   * @return newly created Node
   */
  def createNewNode(): Node = {
    if (this.template(this.parsingInfo.idx + 1) == '?') {
      val n = new ProcessingNode(parent = this.parsingInfo.currentNode)
      this.parsingInfo.currentNode.addChild(n)
      this.parsingInfo.currentNode = n
      this.parsingInfo.moveIndex(2)
      this.parsingInfo.state = ParsingStates.READ_NODE_NAME
      n
    } else if (this.template(this.parsingInfo.idx + 1) == '!') {
      val n = new DirectiveNode(parent = this.parsingInfo.currentNode)
      this.parsingInfo.currentNode.addChild(n)
      this.parsingInfo.currentNode = n
      this.parsingInfo.moveIndex(2)
      this.parsingInfo.state = ParsingStates.READ_NODE_NAME
      n
    } else {
      val n = new Node(parent = this.parsingInfo.currentNode, name = "")
      this.parsingInfo.currentNode.addChild(n)
      this.parsingInfo.currentNode = n
      if (n.children.nonEmpty) {
        /*
        This is here just in case. There was an issue with Python's runtime because it did NOT create
        Nodes properly and list of children had to be created manually or the children would leak to
        unrelated objects.
        */
        throw new Error("Memory is leaking here again")
      }
      this.parsingInfo.state = ParsingStates.READ_NODE_NAME
      this.parsingInfo.moveIndex()
      n
    }
  }

  /**
   * This function is called when state is ParsingStates.NEW_PAGE and "<" was encountered.
   */
  def startingCharOnNewPage(): Unit = {
    if (this.template.substring(this.parsingInfo.idx).indexOf("<?xml") == 0) {
      parsingInfo.moveIndex("<?xml".length)
      parsingInfo.state = ParsingStates.LOOKING_FOR_ATTRIBUTE
    } else if (this.template.substring(this.parsingInfo.idx).indexOf("<!DOCTYPE") == 0) {
      this.parsingInfo.currentNode match {
        case node: RootNode => {
          node.html = true
          this.parsingInfo.currentNode.setAttribute(
            "doctype",
            this.template.substring(
              this.parsingInfo.idx + "<!DOCTYPE ".length,
              this.template.indexOf(">")
            ))
          this.parsingInfo.state = ParsingStates.LOOKING_FOR_CHILD_NODES
          this.parsingInfo.moveIndex(this.template.indexOf(">"))
        }
      }
    } else {
      this.parsingInfo.currentNode = this.createNewNode()
      this.parsingInfo.state = ParsingStates.READ_NODE_NAME
    }
  }

  /**
   * This function is called when state is ParsingStates.LOOKING_FOR_CHILD_NODES and "<" was encountered.
   */
  def startingCharLookingForChildNodes(): Unit = {
    if (this.template.substring(this.parsingInfo.idx).indexOf("<![CDATA[") == 0) {
      this.parsingInfo.moveIndex("<![CDATA[".length)
      val tn = new TextNode(
        parent = this.parsingInfo.currentNode,
        cdata = true,
        content = this.template.substring(
          this.parsingInfo.idx,
          this.template.substring(this.parsingInfo.idx).indexOf("]]>")
        )
      )
      this.parsingInfo.currentNode.addChild(tn)
      this.parsingInfo.moveIndex(s"${tn.content}]]>".length)
    } else if (this.template.substring(this.parsingInfo.idx).indexOf("<!--") == 0) {
      this.parsingInfo.moveIndex("<![CDATA[".length)
      val cn = new CommentNode(
        parent = this.parsingInfo.currentNode,
        content = this.template.substring(
          this.parsingInfo.idx,
          this.template.substring(this.parsingInfo.idx).indexOf("-->")
        )
      )
      this.parsingInfo.currentNode.addChild(cn)
      this.parsingInfo.moveIndex(s"${cn.content}-->".length)
    } else if (this.template(this.parsingInfo.idx + 1) == '/') {
      val name = this.template.substring(this.parsingInfo.idx + 2, this.parsingInfo.idx + 2 + this.template.substring(this.parsingInfo.idx + 2).indexOf(">"))
      if (this.parsingInfo.currentNode.name == name) {
        this.parsingInfo.currentNode = parsingInfo.currentNode.parent
        this.parsingInfo.moveIndex(s"</${name}>".length)
      } else {
        throw new XMLParsingException("Need to test this thoroughly")
      }
    } else {
      this.parsingInfo.state = ParsingStates.READ_NODE_NAME
      this.createNewNode()
    }
  }

  /**
   * Function that handles processing ">" character
   */
  def parseEndingTagCharacter(): Unit = {
    if (this.parsingInfo.state == ParsingStates.LOOKING_FOR_ATTRIBUTE) {
      if ((this.template.substring(this.parsingInfo.idx - 1) == "/" || !this.parsingInfo.currentNode.isPairedTag)
        && !this.parsingInfo.currentNode.isInstanceOf[RootNode]) {
        this.parsingInfo.currentNode.argPairedTag = false
        this.parsingInfo.currentNode = this.parsingInfo.currentNode.parent
      }
      this.parsingInfo.state = ParsingStates.LOOKING_FOR_CHILD_NODES

      if (this.parsingInfo.currentNode.name.toLowerCase != "script") {
        this.parsingInfo.moveIndex()
      } else {
        val endScriptPosition = this.parsingInfo.idx + this.template.substring(this.parsingInfo.idx).indexOf("</script>")
        if (endScriptPosition < this.parsingInfo.idx) {
          throw new XMLParsingException("Script attribute not ended")
        }
        val tn = new TextNode(
          cdata = false,
          content = this.template.substring(this.parsingInfo.idx + 1, endScriptPosition),
          parent = this.parsingInfo.currentNode
        )
        this.parsingInfo.currentNode.addChild(tn)
        this.parsingInfo.moveIndex(
          s"${this.template.substring(this.parsingInfo.idx, endScriptPosition)}</script>".length
        )
        this.parsingInfo.currentNode = this.parsingInfo.currentNode.parent
      }
    } else {
      this.parsingInfo.moveIndex()
    }
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

  /**
   * Function processes adding child text node
   */
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

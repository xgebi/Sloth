package templating.XMLParser

import templating.exceptions.EmptyTemplateException
import templating.nodes._

object XMLParser {
  def parse(template: String): Node = {
    if (template.isEmpty) {
      throw new EmptyTemplateException("template cannot be empty")
    }

  }
}

package templating

import templating.toe.Hooks

import java.nio.file.Path
import scala.collection.mutable

object TemplateEngine {
  def render_toe(template: String, data: mutable.HashMap[String, String], hooks: List[Hooks]): String = {

    ""
  }

  def render_toe(template: Path, data: mutable.HashMap[String, String], hooks: List[Hooks]): String = {
    ""
  }
}

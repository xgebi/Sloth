import com.sloth.app._
import org.mindrot.jbcrypt.BCrypt
import org.scalatra._

import javax.servlet.ServletContext

class ScalatraBootstrap extends LifeCycle {
  override def init(context: ServletContext) {
    context.mount(new SlothServlet, "/*")
    context.mount(new ContentManagementServlet, "/content")
  }
}

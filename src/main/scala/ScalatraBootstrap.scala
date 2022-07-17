import com.mchange.v2.c3p0.ComboPooledDataSource
import com.sloth.app._
import com.sloth.app.servlets.{ContentManagementServlet, SlothServlet}
import org.mindrot.jbcrypt.BCrypt
import org.scalatra._
import org.slf4j.{Logger, LoggerFactory}
import slick.jdbc.PostgresProfile.api._

import javax.servlet.ServletContext

class ScalatraBootstrap extends LifeCycle {
  val logger: Logger = LoggerFactory.getLogger(getClass)

  val cpds = new ComboPooledDataSource
  logger.info("Created c3p0 connection pool")

  override def init(context: ServletContext): Unit = {
    DbClient.db = Some(Database.forDataSource(cpds, None))

    context.mount(new SlothServlet, "/*")
    context.mount(new ContentManagementServlet, "/content")
  }

  private def closeDbConnection(): Unit = {
    logger.info("Closing c3po connection pool")
    cpds.close()
  }

  override def destroy(context: ServletContext): Unit = {
    super.destroy(context)
    closeDbConnection()
  }
}

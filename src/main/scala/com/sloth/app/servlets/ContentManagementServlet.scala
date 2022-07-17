package com.sloth.app.servlets

import com.sloth.app.DbClient
import com.sloth.app.services.ContentManagementService
import org.scalatra._
import slick.jdbc.PostgresProfile.api._

class ContentManagementServlet extends ScalatraServlet {

  delete("/clear") {
    val cms = new ContentManagementService()
    cms.deleteAllContent()
    response.setStatus(204)
  }

}

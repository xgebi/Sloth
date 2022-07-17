package com.sloth.app.servlets

import com.sloth.app.DbClient
import com.sloth.app.services.ContentManagementService
import org.scalatra._
import slick.jdbc.PostgresProfile.api._

class ContentManagementServlet(val contentManagementService: ContentManagementService = new ContentManagementService()) extends ScalatraServlet {

  delete("/clear") {
    try {
      this.contentManagementService.deleteAllContent()
      response.setStatus(204)
    } catch {
      case _: Exception => response.setStatus(500)
    }
  }

}

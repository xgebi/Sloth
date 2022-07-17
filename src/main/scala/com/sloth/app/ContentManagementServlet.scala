package com.sloth.app

import org.scalatra._

class ContentManagementServlet extends ScalatraServlet {

  delete("/clear") {
    response.setStatus(204)
  }

}

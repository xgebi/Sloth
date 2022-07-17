package com.sloth.app.servlets

import org.scalatra._

class SlothServlet extends ScalatraServlet {

  get("/") {
    views.html.hello()
  }

}

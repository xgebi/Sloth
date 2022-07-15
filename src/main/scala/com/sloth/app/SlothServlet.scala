package com.sloth.app

import org.scalatra._

class SlothServlet extends ScalatraServlet {

  get("/") {
    views.html.hello()
  }

}

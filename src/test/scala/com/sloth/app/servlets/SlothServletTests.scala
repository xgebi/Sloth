package com.sloth.app.servlets

import org.scalatra.test.scalatest._

class SlothServletTests extends ScalatraFunSuite {


  addServlet(classOf[SlothServlet], "/*")

  test("GET / on SlothServlet should return status 200") {
    get("/") {
      status should equal (200)
    }
  }

  override def header = ???
}

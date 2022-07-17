package com.sloth.app

import org.scalatra.test.scalatest._

class ContentManagementServletTests extends ScalatraFunSuite {


  addServlet(classOf[ContentManagementServlet], "/*")

  test("DELETE /clear on ContentManagementServlet should return status 204") {
    delete("/clear") {
      status should equal (204)
    }
  }

  override def header = ???
}

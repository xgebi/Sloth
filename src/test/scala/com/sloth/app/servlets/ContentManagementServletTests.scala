package com.sloth.app.servlets

import com.sloth.app.ContentManagementServlet
import com.sloth.app.services.ContentManagementService
import org.mockito.Mockito._
import org.scalatra.test.scalatest._

class ContentManagementServletTests extends ScalatraFunSuite {

  addServlet(classOf[ContentManagementServlet], "/*")

  test("DELETE /clear on ContentManagementServlet should return status 204") {
    delete("/clear") {
      val cmsMocked = mock(classOf[ContentManagementService])
      when(cmsMocked.deleteAllContent()).thenReturn(true)
      status should equal(204)
    }
  }

  override def header = ???
}

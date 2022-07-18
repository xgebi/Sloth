package com.sloth.templating.toes

import com.sloth.templating.toe.VariableWrapper
import org.scalatest.funspec.AnyFunSpec
import scala.collection.mutable

class VariableWrapperTests extends AnyFunSpec {
  it("VariableWrapper was created") {
    val vw = new VariableWrapper(1, 1.getClass)
    assert(vw != null)
  }

  describe("resolve") {
    it("resolves an integer") {
      val vw = new VariableWrapper(1, 1.getClass)
      assert(vw != null)

      assert(vw.resolve(null) == 1)
    }

    it("resolves a list") {
      val l = List("abc")
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.resolve(List("0")) == "abc")
    }
  }

  describe("is iterable") {
    it("integer is not iterable") {
      val vw = new VariableWrapper(1, 1.getClass)
      assert(vw != null)

      assert(!vw.isIterable(1.getClass))
    }

    it("HashMap is iterable") {
      val hm = mutable.HashMap()
      val vw = new VariableWrapper(hm, hm.getClass)
      assert(vw != null)

      assert(vw.isIterable(hm.getClass))
    }

    it("List is iterable") {
      val l = List()
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.isIterable(l.getClass))
    }
  }
}

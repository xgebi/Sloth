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

    it("resolves a simple list") {
      val l = List("abc")
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.resolve(List("0")) == "abc")
    }

    it("resolves a list with nested list") {
      val l = List(List("abc"))
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.resolve(List("0", "0")) == "abc")
    }

    it("resolves a list with nested HashMap") {
      val l = List(mutable.HashMap("abc" -> "def"))
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.resolve(List("0", "abc")) == "def")
    }

    it("resolves a simple HashMap") {
      val l: mutable.HashMap[String, Any] = mutable.HashMap("a" -> 1)
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.resolve(List("a")) == 1)
    }

    it("resolves a HashMap with nested list") {
      val l: mutable.HashMap[String, Any] = mutable.HashMap("a" -> List(2))
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.resolve(List("a", "0")) == 2)
    }

    it("resolves a HashMap with nested HashMap") {
      val l: mutable.HashMap[String, Any] = mutable.HashMap("a" -> mutable.HashMap("b" -> 2))
      val vw = new VariableWrapper(l, l.getClass)
      assert(vw != null)

      assert(vw.resolve(List("a", "b")) == 2)
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

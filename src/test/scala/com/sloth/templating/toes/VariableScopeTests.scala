package com.sloth.templating.toes

import com.sloth.templating.exceptions.VariableScopeException
import com.sloth.templating.toe.{VariableScope, VariableWrapper}
import org.scalatest.funspec.AnyFunSpec

import scala.collection.mutable

class VariableScopeTests extends AnyFunSpec{
  describe("find variable") {
    it("variable found in current scope") {

    }

    it("variable not found") {

    }

    it("variable found in parent scope") {

    }
  }

  describe("get names") {
    it("parses: name") {
      val vs = new VariableScope()
      val result = vs.getNames(name = "name")
      assert(result.length == 1)
      assert(result.head == "name")
    }

    it("parses: name['abc']") {
      val vs = new VariableScope()
      val result = vs.getNames(name = "name['abc']")
      assert(result.length == 2)
      assert(result.head == "name")
      assert(result(1) == "'abc'")
    }

    it("parses: name[1]") {
      val vs = new VariableScope()
      val result = vs.getNames(name = "name[1]")
      assert(result.length == 2)
      assert(result.head == "name")
      assert(result(1) == "1")
    }

    it("parses: name[1][0]") {
      val vs = new VariableScope()
      val result = vs.getNames(name = "name[1][0]")
      assert(result.length == 3)
      assert(result.head == "name")
      assert(result(1) == "1")
      assert(result(2) == "0")
    }

    it("parses: name['abc'][0]") {
      val vs = new VariableScope()
      val result = vs.getNames(name = "name['abc'][0]")
      assert(result.length == 3)
      assert(result.head == "name")
      assert(result(1) == "'abc'")
      assert(result(2) == "0")
    }
  }

  describe("assign variable") {
    it("assign value to variable in the current scope") {

    }

    it("assign value to variable in the parent scope") {

    }

    it("throws error when variable doesn't exist") {

    }
  }

  describe("create a variable") {
    it("creates a variable") {
      val vw = new VariableWrapper(1)
      val vs = new VariableScope()
      vs.createVariable("a", vw)
      assert(vs.variables.contains("a"))
    }

    it("throws error when variable in current scope already exists") {
      val vw = new VariableWrapper(1)
      val vs = new VariableScope(mutable.HashMap("a" -> vw))
      assertThrows[VariableScopeException] {
        vs.createVariable("a", "1")
      }
    }
  }

  describe("is variable in current scope") {
    it("variable found in current scope") {
      val vw = new VariableWrapper(1)
      val vs = new VariableScope(mutable.HashMap("a" -> vw))
      assert(vs.isVariableInCurrentScope("a"))
    }

    it("variable not found") {
      val vs = new VariableScope()
      assert(!vs.isVariableInCurrentScope("a"))
    }
  }

  describe("does variable exist") {
    it("variable found in current scope") {

    }

    it("variable not found") {

    }

    it("variable found in parent scope") {

    }
  }
}

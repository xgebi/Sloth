package com.sloth.templating.toe

import com.sloth.templating.exceptions.VariableScopeException

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

class VariableScope(
                     val variables: mutable.HashMap[String, VariableWrapper] = mutable.HashMap(),
                     val parentScope: Option[VariableScope] = None
                   ) {
  /**
   * Function for resolving a variable
   *
   * @param name Name of the variable
   * @param originalScope starting scope of the search ???
   * @param passedNames I don't know yet, I don't remember
   * @return Returns value of a variable as a string
   */
  def findVariable(name: String, originalScope: Option[VariableScope], passedNames: Option[List[String]]): Any = {
    val names: List[String] = {
      if (passedNames.nonEmpty) {
        passedNames.get
      } else {
        this.getNames(name = name).toList
      }
    }

    if (names.nonEmpty) {
      if (this.isVariableInCurrentScope(names.head)) {
        this.variables(names.head).resolve(passedNames.get.tail)
      } else if (this.parentScope.nonEmpty) {
        this.parentScope.get.findVariable(name, originalScope, passedNames)
      } else {
        throw new VariableScopeException(s"Variable ${names.head} was not found")
      }
    } else {
      throw new VariableScopeException(s"Variable ${names.head} was not found")
    }
  }

  /**
   * To be determined, most likely for stuff like objects
   *
   * @param name Name of the variable
   * @param passedNames I don't know yet, I don't remember
   * @return
   */
  def getNames(name: String, passedNames: Option[ListBuffer[String]] = Some(ListBuffer())): ListBuffer[String] = {
    if (passedNames.get.isEmpty && name.indexOf("[") >= 0) {
      var idx = name.indexOf("[") + 1
      passedNames.get.addOne(name.substring(0, idx - 1))
      var level = 1
      var temp = ""
      while (idx < name.length) {
        if (name(idx) == '[') {
          if (level == 0) {
            passedNames.get.addOne(temp)
            temp = ""
          } else {
            temp += name(idx)
          }
          level += 1
        } else if (name(idx) == ']') {
          if (level > 1) {
            temp += name(idx)
          }
          level -= 1
        } else {
          temp += name(idx)
        }
        idx += 1
        if (idx < name.length && level == -1) {
          return null
        }
      }
      passedNames.get.addOne(temp)
    } else {
      return ListBuffer(name)
    }
    passedNames.get
  }

  /**
   * Assigns value to an existing variable
   *
   * @param name Name of the variable
   * @param value Value of the variable
   */
  def assignVariable(name: String, value: Any): Unit = {
    if (this.isVariableInCurrentScope(name)) {
      val vw = new VariableWrapper(value = value)
      this.variables.update(name, vw)
    } else if (this.parentScope.nonEmpty) {
      this.parentScope.get.assignVariable(name, value)
    } else {
      throw new VariableScopeException("Variable doesn't exist")
    }

  }

  /**
   * Creates a new variable
   *
   * @param name Name of the variable
   * @param value Value of the variable
   */
  def createVariable(name: String, value: Any): Unit = {
    if (this.isVariableInCurrentScope(name)) {
      throw new VariableScopeException(s"Variable $name already exists")
    }
    this.variables.addOne(name, new VariableWrapper(value = value))
  }

  /**
   * Function for checking if variable exists
   *
   * @param name Name of the variable
   * @param originalScope starting scope of the search ???
   * @param passedNames I don't know yet, I don't remember
   * @return Returns value of a variable as a string
   */
  def variableExists(name: String, originalScope: Option[VariableScope], passedNames: Option[List[String]]): Boolean = {
    if (this.findVariable(name, originalScope, passedNames) != null) {
      true
    } else {
      false
    }
  }

  /**
   * Checks if variable is in current scope
   *
   * @param name Name of the variable
   * @return returns true if variable is in current scope
   */
  def isVariableInCurrentScope(name: String): Boolean = {
    this.variables.contains(name)
  }

}

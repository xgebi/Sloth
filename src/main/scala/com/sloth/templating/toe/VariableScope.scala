package com.sloth.templating.toe

import scala.collection.mutable

class VariableScope(
                     val variables: mutable.HashMap[String, String] = mutable.HashMap(),
                     val parentScope: VariableScope = null
                   ) {
  /**
   * Function for resolving a variable
   *
   * @param name Name of the variable
   * @param originalScope starting scope of the search ???
   * @param passedNames I don't know yet, I don't remember
   * @return Returns value of a variable as a string
   */
  def findVariable(name: String, originalScope: VariableScope, passedNames: List[String]): String = {
    ""
  }

  /**
   * To be determined, most likely for stuff like objects
   *
   * @param name Name of the variable
   * @param passedNames I don't know yet, I don't remember
   * @return
   */
  def getNames(name: String, passedNames: List[String]): Any = {

  }

  /**
   * Assigns value to an existing variable
   *
   * @param name Name of the variable
   * @param value Value of the variable
   */
  def assignVariable(name: String, value: String): Unit = {

  }

  /**
   * Creates a new variable
   *
   * @param name Name of the variable
   * @param value Value of the variable
   */
  def createVariable(name: String, value: String): Unit = {

  }

  /**
   * Function for checking if variable exists
   *
   * @param name Name of the variable
   * @param originalScope starting scope of the search ???
   * @param passedNames I don't know yet, I don't remember
   * @return Returns value of a variable as a string
   */
  def variableExists(name: String, originalScope: VariableScope, passedNames: List[String]): String = {
    ""
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

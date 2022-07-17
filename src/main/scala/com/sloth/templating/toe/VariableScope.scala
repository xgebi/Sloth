package com.sloth.templating.toe

import com.sloth.templating.exceptions.VariableScopeException

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

class VariableScope(
                     val variables: mutable.HashMap[String, String] = mutable.HashMap(),
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
  def findVariable(name: String, originalScope: Option[VariableScope], passedNames: Option[List[String]]): String = {
    val names: List[String] = {
      if (passedNames.nonEmpty) {
        passedNames.get
      } else {
        this.getNames(name = name).toList
      }
    }


    /*
		if len(names) > 0 and self.is_variable(variable_name=names[0], original_scope=original_scope):
			if len(names) > 0:
				if names[0] in self.variables:
					res = self.variables.get(names[0])
				elif self.parent_scope is not None:
					res = self.parent_scope.find_variable(names[0], names, self if original_scope is None else original_scope)
				else:
					return None
				if (type(res) is list and len(res) > 0) or type(res) is dict:
					for i in range(1, len(names)):
						if ((names[i][0] == "'" and names[i][-1] == "'") or (names[i][0] == "\"" and names[i][-1] == "\"")) \
								and names[i].find("+") == -1:
							resolved_name = names[i][1: -1]
						else:
							try:
								resolved_name = int(names[i])
							except:
								resolved_name = self.find_variable(names[i], original_scope=original_scope)
						if resolved_name in res or (type(resolved_name) is int and len(res) > resolved_name and res[resolved_name] is not None):
							res = res[resolved_name]
						elif original_scope is not None:
							return original_scope.find_variable(variable_name=variable_name)
						else:
							return None
				return res
			else:
				return self.variables[names[0]]

		return None
     */
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
  def assignVariable(name: String, value: String): Unit = {
    if (this.isVariableInCurrentScope(name)) {
      this.variables.update(name, value)
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
  def createVariable(name: String, value: String): Unit = {
    if (this.isVariableInCurrentScope(name)) {
      throw new VariableScopeException(s"Variable $name already exists")
    }
    this.variables.addOne(name, value)
  }

  /**
   * Function for checking if variable exists
   *
   * @param name Name of the variable
   * @param originalScope starting scope of the search ???
   * @param passedNames I don't know yet, I don't remember
   * @return Returns value of a variable as a string
   */
  def variableExists(name: String, originalScope: VariableScope, passedNames: List[String]): Boolean = {
    true
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

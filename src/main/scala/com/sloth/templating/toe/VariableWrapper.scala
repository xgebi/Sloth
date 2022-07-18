package com.sloth.templating.toe

import scala.collection.mutable

class VariableWrapper(val value: Any, val variableType: Class[_]) {
  def resolve(passedNames: List[String]): Any = {
    if (this.isIterable(variableType)) {
      var currentlyResolved:Any = value
      passedNames.foreach((name: String) => {
        if (classOf[mutable.HashMap[String, Any]].isAssignableFrom(variableType)) {
          println(s"HashMap $name")
        } else if (classOf[List[Any]].isAssignableFrom(variableType)) {
          currentlyResolved = currentlyResolved.asInstanceOf[List[Any]].toList(name.toInt)
        }
      })
      currentlyResolved
    } else {
      value
    }
  }

  def isIterable(c:Class[_]): Boolean = classOf[Iterable[_]].isAssignableFrom(c)
}

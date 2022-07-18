package com.sloth.templating.toe

import com.sloth.templating.exceptions.VariableResolvingException

import scala.collection.mutable

class VariableWrapper(val value: Any) {
  def resolve(passedNames: List[String]): Any = {
    if (this.isIterable(this.value.getClass)) {
      var currentlyResolved:Any = value
      passedNames.foreach((name: String) => {
        currentlyResolved match {
          case hm: mutable.HashMap[String, Any] => currentlyResolved = hm(name)
          case l: List[Any] => currentlyResolved = l(name.toInt)
          case _ => throw new VariableResolvingException(s"Stopped resolving a variable at $name")
        }
      })
      currentlyResolved
    } else {
      value
    }
  }

  def isIterable(c:Class[_]): Boolean = classOf[Iterable[_]].isAssignableFrom(c)
}

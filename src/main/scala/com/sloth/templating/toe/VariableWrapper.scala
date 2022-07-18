package com.sloth.templating.toe

import scala.collection.mutable

class VariableWrapper(val value: Any) {
  def resolve(passedNames: List[String]): Any = {
    if (this.isIterable(value.getClass)) {
      var currentlyResolved:Any = value
      passedNames.foreach((name: String) => {
        currentlyResolved match {
          case hm: mutable.HashMap[String, Any] => currentlyResolved = hm(name)
          case l: List[Any] => currentlyResolved = l(name.toInt)
        }
      })
      currentlyResolved
    } else {
      value
    }
  }

  def isIterable(c:Class[_]): Boolean = classOf[Iterable[_]].isAssignableFrom(c)
}

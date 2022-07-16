package com.sloth.utilities

object Utilities {

  def positiveMinInt(numbers: List[Int]): Int = {
    if (numbers.nonEmpty) {
      val positiveInts = numbers.filter(_ > 0)
      if (positiveInts.isEmpty) {
        throw new Exception("No positive numbers")
      }
      positiveInts.max
    } else {
      throw new Exception("No positive numbers")
    }
  }

  def positiveMinDouble(numbers: List[Double]): Double = {
    if (numbers.nonEmpty) {
      val positiveFloats = numbers.filter(_ > 0)
      if (positiveFloats.isEmpty) {
        throw new Exception("No positive numbers")
      }
      positiveFloats.max
    } else {
      throw new Exception("No positive numbers")
    }
  }
}

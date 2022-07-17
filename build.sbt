import sbt.Keys.libraryDependencies

val ScalatraVersion = "2.8.2"

ThisBuild / scalaVersion := "2.13.4"
ThisBuild / organization := "com.sloth"

lazy val hello = (project in file("."))
  .settings(
    name := "Sloth",
    version := "2.0.0-REBUILD",
    libraryDependencies ++= Seq(
      "org.scalatra" %% "scalatra" % ScalatraVersion,
      "org.scalatra" %% "scalatra-scalatest" % ScalatraVersion % "test",
      "ch.qos.logback" % "logback-classic" % "1.2.3" % "runtime",
      "org.eclipse.jetty" % "jetty-webapp" % "9.4.35.v20201120" % "container",
      "javax.servlet" % "javax.servlet-api" % "3.1.0" % "provided",
      "org.json4s"   %% "json4s-jackson" % "4.0.1",
      "com.typesafe.slick" %% "slick" % "3.3.3",
      "org.slf4j" % "slf4j-nop" % "1.6.4",
      "org.postgresql" % "postgresql" % "42.4.0",
      "com.mchange" % "c3p0" % "0.9.5.5"
    ),
    libraryDependencies += "org.mockito" % "mockito-scala_2.13" % "1.17.7",
    libraryDependencies += "org.bitbucket.b_c" % "jose4j" % "0.7.12",
    // For the time being there shall be argon and bcrypt at the same time
    libraryDependencies += "de.mkammerer" % "argon2-jvm" % "2.11",
    libraryDependencies += "org.mindrot" % "jbcrypt" % "0.4"
  )

enablePlugins(SbtTwirl)
enablePlugins(JettyPlugin)

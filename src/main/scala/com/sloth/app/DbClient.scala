package com.sloth.app

import slick.jdbc.PostgresProfile.api._

object DbClient {
  var db: Option[Database] = None
}

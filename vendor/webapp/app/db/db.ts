import postgres from 'postgres'

const sql = postgres(`postgres://${process.env["DATABASE_URL"]}:${process.env["DATABASE_PORT"]}/${process.env["DATABASE_NAME"]}`, {
  username             : process.env["DATABASE_USER"],            // Username of database user
  password             : process.env["DATABASE_PASSWORD"],            // Password of database user
})

export default sql
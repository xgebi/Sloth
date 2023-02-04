use postgres::{Client, Error, NoTls};
use dotenv::dotenv;
use std::env;

pub fn connect() -> Result<Client, Error> {
    dotenv().ok();
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    Client::connect("host=localhost user=postgres", NoTls)
}

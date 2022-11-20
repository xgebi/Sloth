mod pgs_config;

use ::config::Config;
use dotenv::dotenv;
use tokio_postgres::NoTls;


#[actix_web::main]
fn main() {
    dotenv().ok();

    let config_ = Config::builder()
        .add_source(::config::Environment::default())
        .build()
        .unwrap();

    let config: pgs_config::PGSConfig = config_.try_deserialize().unwrap();

    let pool = config.pg.create_pool(None, NoTls).unwrap();

    println!("Hello, world!");
}

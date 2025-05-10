mod config_app;
mod render;

use actix_web::{middleware, web, App, HttpServer};
use crate::config_app::config_app;


#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    log::info!("starting HTTP server at http://localhost:8080");

    HttpServer::new(|| {
        App::new()
            // enable logger
            .wrap(middleware::Logger::default())
            // .service(Files::new("/assets", "static/"))
            .configure(config_app)
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}
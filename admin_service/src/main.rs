mod authentication;
mod guards;
mod dashboard;
mod themes;
mod post_type;
mod post;
mod settings;
mod user;

use actix_web::{App, guard, HttpServer, middleware, web};
use crate::authentication::{process_login, serve_login_page};
use crate::authentication::authentication::{process_login, serve_login_page};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .wrap(middleware::NormalizePath::default())
            .service(web::resource("/login").route(web::get().to(serve_login_page)))
            .service(web::resource("/login").route(web::post().guard(guard::Header("content-type", "application/json")).to(process_login)))
            .service(web::resource("/").route(web::post().to(process_login)))
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}

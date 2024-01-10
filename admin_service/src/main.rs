mod authentication;
mod guards;
mod dashboard;
mod themes;
mod post_type;
mod post;
mod settings;
mod user;
mod media;

use tonic;
use actix_web::{App, guard, HttpServer, middleware, web};
use crate::authentication::authentication::{process_login, serve_login_page};
use crate::guards::LoggedInGuard;

pub mod page_generation {
    tonic::include_proto!("page_generation"); // The string specified here must match the proto package name
}

pub mod auth_service {
    tonic::include_proto!("auth_service"); // The string specified here must match the proto package name
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {

    HttpServer::new(|| {
        App::new()
            .wrap(middleware::NormalizePath::default())
            .service(web::resource("/login").route(web::get().to(serve_login_page)))
            .service(web::resource("/login").route(web::post().guard(guard::Header("content-type", "application/json")).to(process_login)))
            .service(web::resource("/").route(web::post().guard(LoggedInGuard).to(process_login)))
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}

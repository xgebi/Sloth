mod authentication;

use actix_web::{App, HttpServer, web};
use crate::authentication::{process_login, serve_login_page};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(web::resource("/login").route(web::get().to(serve_login_page)))
            .service(web::resource("/login").route(web::post().to(process_login)))
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}

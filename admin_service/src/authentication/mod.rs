use actix_web::{Error, HttpResponse, web};
use deadpool_postgres::Pool;
use tokio_postgres::Client;

pub(crate) mod authentication;

pub async fn serve_login_page(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
        todo!("Should serve login page")
    }

pub async fn process_login(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
        todo!("Should process login")
    }
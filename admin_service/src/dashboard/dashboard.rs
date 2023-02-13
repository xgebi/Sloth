use actix_web::{Error, HttpResponse, web};
use deadpool_postgres::Pool;

pub async fn redirect_to_dashboard(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
    Ok(HttpResponse::Found().append_header(("Location", "/dashboard")).finish())
}

pub async fn serve_dashboard_page(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
    todo!("Should serve dashboard page")
}
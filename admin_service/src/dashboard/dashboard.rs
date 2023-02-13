use actix_web::{Error, HttpResponse, Responder, web};
use deadpool_postgres::Pool;

pub async fn redirect_to_dashboard(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> impl Responder {
    web::Redirect::to("/dashboard").see_other()
}

pub async fn serve_dashboard_page(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
    todo!("Should serve dashboard page")
}
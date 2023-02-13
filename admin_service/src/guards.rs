use actix_web::guard::GuardContext;
use actix_web::HttpResponse;

async fn login_guard(req: &GuardContext) -> HttpResponse {
    if token.is_none() {
        HttpResponse::Found().append_header(("Location", "/login")).finish()
    } else {
        HttpResponse::Ok().finish()
    }
}
use actix_web::guard::GuardContext;
use actix_web::web;
use crate::render::render;

fn check_token_guard(ctx: &GuardContext) -> bool {
    true
}

pub fn config_app(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/render")
            .guard(check_token_guard)
            .service(
                web::resource("")
                    .route(web::post().to(render))
            )
    );
}
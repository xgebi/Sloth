use std::net::ToSocketAddrs;
use actix_web::guard::{GuardContext, Guard};
use actix_web::HttpResponse;
use actix_web::rt::Runtime;
use actix_web_lab::__reexports::futures_util::{future, SinkExt, TryFutureExt};
use async_trait::async_trait;
use sloth_config_lib::get_config;
use crate::auth_service::auth_service_client::AuthServiceClient;
use crate::auth_service::LoggedInRequest;

pub struct LoggedInGuard;

impl Guard for LoggedInGuard {
    fn check(&self, ctx: &GuardContext<'_>) -> bool {
        let context = ctx.clone();
        let mut token = "".to_string();

        if context.head().headers.contains_key("authorization") {
                token = context.head().headers.get("authorization").unwrap().to_str().unwrap().to_string();
        } else if context.head().headers.contains_key("Authorization") {
                token = context.head().headers.get("Authorization").unwrap().to_str().unwrap().to_string();
        }

        if !token.is_empty() {
            return Runtime::new().unwrap().block_on(check_logged_in(token));
        }
        false
    }
}

async fn check_logged_in(mut token: String) -> bool {
    let conf = get_config();
    if let Ok(config) = conf {
        let client_details = format!("{}:{}", config.auth_service.url, config.auth_service.port);
        let client_result = AuthServiceClient::connect(client_details).await;
        if let Ok(mut auth_service) = client_result {
            let request = tonic::Request::new(LoggedInRequest {
                token: token.to_string(),
            });
            let response = auth_service.is_logged_in(request).await;
            if let Ok(r) = response {
                return r.into_inner().result;
            }
        }
    }
    false
}

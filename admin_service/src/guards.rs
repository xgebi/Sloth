use std::net::ToSocketAddrs;
use actix_web::guard::{GuardContext, Guard};
use actix_web::HttpResponse;
use async_trait::async_trait;
use sloth_config_lib::get_config;
use crate::auth_service::auth_service_client::AuthServiceClient;
use crate::auth_service::LoggedInRequest;

pub struct LoggedInGuard;

#[async_trait]
impl Guard for LoggedInGuard {
    async fn check<'a>(&self, ctx: &'a GuardContext<'a>) -> bool {
        let context = ctx.clone();
        let headers = context.head().headers();
        let mut token = "";

        let x = context.head()
                .headers()
                .get("Accept-Version").unwrap().to_str();

        if let Some(t) = headers.get("authorization") {
            if let Ok(local) = t.to_str() {
                token = local;
            }
        } else if let Some(t) = headers.get("Authorization") {
            if let Ok(local) = t.to_str() {
                token = local;
            }
        }
        if !token.is_empty() {
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
        }
        false
    }
}
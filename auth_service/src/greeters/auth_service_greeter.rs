use tonic::{Request, Response, Status, async_trait};
use crate::auth_service::auth_service_server::AuthService;
use crate::auth_service::{LoginRequest, LoginResponse, LogoutRequest, LogoutResponse, PasswordChangeRequest, PasswordChangeResponse, PasswordCreationRequest, PasswordCreationResponse};

#[derive(Debug, Default)]
pub struct AuthServiceGreeter {}

#[async_trait]
impl AuthService for AuthServiceGreeter {
    async fn login(&self, request: Request<LoginRequest>) -> Result<Response<LoginResponse>, Status> {

        let reply = LoginResponse {
            token: "abc".to_string(),
            expiration: 1234,
        };
        Ok(Response::new(reply))
    }

    async fn logout(&self, request: Request<LogoutRequest>) -> Result<Response<LogoutResponse>, Status> {
        todo!()
    }

    async fn change_password(&self, request: Request<PasswordChangeRequest>) -> Result<Response<PasswordChangeResponse>, Status> {
        todo!()
    }

    async fn create_password(&self, request: Request<PasswordCreationRequest>) -> Result<Response<PasswordCreationResponse>, Status> {
        todo!()
    }
}
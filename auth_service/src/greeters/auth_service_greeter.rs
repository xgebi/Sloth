use tonic::{Request, Response, Status, async_trait};
use crate::auth_service::auth_service_server::AuthService;
use crate::auth_service::{LoginRequest, LoginResponse, LogoutRequest, LogoutResponse, PasswordChangeRequest, PasswordChangeResponse, PasswordCreationRequest, PasswordCreationResponse};
use crate::database::fetch_hash;

#[derive(Debug, Default)]
pub struct AuthServiceGreeter {}

impl AuthServiceGreeter {
    fn process_bcrypt_login() {

    }

    fn process_argon_login() {

    }
}

#[async_trait]
impl AuthService for AuthServiceGreeter {
    async fn login(&self, request: Request<LoginRequest>) -> Result<Response<LoginResponse>, Status> {
        let login_request = request.into_inner();

        let db_data = fetch_hash(login_request.uuid);
        if let Some(data) = db_data {
            let mut reply = LoginResponse {
                token: "".to_string(),
                expiration: 0,
            };
            if data.0 == "bcrypt" {

            }
            if data.0 == "argon" {

            }
            return Ok(Response::new(reply))
        }
        LoginResponse {
            token: "".to_string(),
            expiration: 0,
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
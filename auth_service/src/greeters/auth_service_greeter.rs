use tonic::{Request, Response, Status, async_trait};
use crate::auth_service::auth_service_server::AuthService;
use crate::auth_service::{LoggedInRequest, LoggedInResponse, LoginRequest, LoginResponse, LogoutRequest, LogoutResponse, PasswordChangeRequest, PasswordChangeResponse, PasswordCreationRequest, PasswordCreationResponse};
use crate::database::fetch_hash;
use crate::authentication::bcrypt;
use crate::authentication::argon;
use crate::authorization::create_token;

#[derive(Debug, Default)]
pub struct AuthServiceGreeter {}

#[async_trait]
impl AuthService for AuthServiceGreeter {
    async fn login(&self, request: Request<LoginRequest>) -> Result<Response<LoginResponse>, Status> {
        let login_request = request.into_inner();

        let db_data = fetch_hash(login_request.uuid.clone());
        let mut reply = LoginResponse {
                token: "".to_string(),
                expiration: 0,
            };
        if let Some(data) = db_data {
            let mut verification_result = false;
            if data.0 == "bcrypt" {
                verification_result = bcrypt::verify_password(login_request.password.clone(), data.1.clone(), login_request.uuid.clone());
            } else if data.0 == "argon" {
                verification_result = argon::verify_password(login_request.password.clone(), data.1.clone(), login_request.uuid.clone());
            }
            if verification_result {
                let res_option = create_token(login_request.uuid.clone());
                if let Some(res) = res_option {
                    reply.token = res.0;
                    reply.expiration = res.1 as u64;
                    return Ok(Response::new(reply));
                }
            }
        }
        Ok(Response::new(reply))
    }

    async fn logout(&self, request: Request<LogoutRequest>) -> Result<Response<LogoutResponse>, Status> {
        todo!()
    }

    async fn is_logged_in(&self, request: Request<LoggedInRequest>) -> Result<Response<LoggedInResponse>, Status> {
        todo!()
    }

    async fn change_password(&self, request: Request<PasswordChangeRequest>) -> Result<Response<PasswordChangeResponse>, Status> {
        todo!()
    }

    async fn create_password(&self, request: Request<PasswordCreationRequest>) -> Result<Response<PasswordCreationResponse>, Status> {
        todo!()
    }
}
use actix_web::guard::{GuardContext, Guard};
use actix_web::HttpResponse;

// async fn login_guard(req: &GuardContext) -> HttpResponse {
//     if token.is_none() {
//         HttpResponse::Found().append_header(("Location", "/login")).finish()
//     } else {
//         HttpResponse::Ok().finish()
//     }
// }

pub struct ApiGuard;

impl Guard for ApiGuard {
    fn check<'a>(&self, ctx: &'a GuardContext<'a>) -> bool {
        let headers = ctx.head().headers();
        let mut token = String::new();
        if let Some(t) = headers.get("authorization") {
            token = t.into();
        } else if let Some(t) = headers.get("Authorization") {
            token = t.into();
        }
        if !token.is_empty() {
            // AuthService::
            // let mut client = GreeterClient::connect("http://[::1]:50051");
            //
            // let request = tonic::Request::new(HelloRequest {
            //     name: "Tonic".into(),
            // });
            //
            // let response = client.say_hello(request).await?;
        }
        false
    }
}
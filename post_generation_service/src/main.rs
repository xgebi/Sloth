use tonic::{transport::Server, Request, Response, Status};

use post_generation::crud_server::{Crud, CrudServer};
use post_generation::{Empty, GeneratingReply, PostRequest };

pub mod post_generation {
    tonic::include_proto!("post_generation"); // The string specified here must match the proto package name
}

#[derive(Debug, Default)]
pub struct MyGreeter {}

#[tonic::async_trait]
impl Crud for MyGreeter {
    async fn generate_post(
        &self,
        request: Request<PostRequest>, // Accept request of type HelloRequest
    ) -> Result<Response<GeneratingReply>, Status> { // Return an instance of type HelloReply
        println!("Got a request: {:?}", request);

        let reply = post_generation::GeneratingReply {
            generating: true
        };

        Ok(Response::new(reply)) // Send back our formatted greeting
    }

    async fn regenerate_all(&self, request: Request<Empty>) -> Result<Response<GeneratingReply>, Status> {
        todo!()
    }

    async fn regenerate_assets(&self, request: Request<Empty>) -> Result<Response<Empty>, Status> {
        todo!()
    }

    async fn is_generating(&self, request: Request<Empty>) -> Result<Response<GeneratingReply>, Status> {
        todo!()
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::1]:50051".parse()?;
    let greeter = MyGreeter::default();

    Server::builder()
        .add_service(CrudServer::new(greeter))
        .serve(addr)
        .await?;

    Ok(())
}
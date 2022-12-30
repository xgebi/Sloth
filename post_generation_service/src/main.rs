mod generator;
mod settings;

use tonic::{transport::Server, Request, Response, Status};

use post_generation::crud_server::{Crud, CrudServer};
use post_generation::{Empty, GeneratingReply, PostRequest };
use crate::generator::{ generate_post, regenerate_all, regenerate_assets, is_generating};

pub mod post_generation {
    tonic::include_proto!("post_generation"); // The string specified here must match the proto package name
}

#[derive(Debug, Default)]
pub struct MyGreeter {}

#[tonic::async_trait]
impl Crud for MyGreeter {
    async fn generate_post(
        &self,
        request: Request<PostRequest>,
    ) -> Result<Response<GeneratingReply>, Status> {
        println!("Got a request: {:?}", request);

        let reply = GeneratingReply {
            generating: generate_post(request.into_inner().uuid)
        };

        Ok(Response::new(reply))
    }

    async fn regenerate_all(&self, _request: Request<Empty>) -> Result<Response<GeneratingReply>, Status> {
        let reply = GeneratingReply {
            generating: regenerate_all()
        };
        Ok(Response::new(reply))
    }

    async fn regenerate_assets(&self, _request: Request<Empty>) -> Result<Response<Empty>, Status> {
        regenerate_assets();
        Ok(Response::new(Empty {}))
    }

    async fn is_generating(&self, _request: Request<Empty>) -> Result<Response<GeneratingReply>, Status> {
        let reply = GeneratingReply {
            generating: is_generating()
        };
        Ok(Response::new(reply))
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
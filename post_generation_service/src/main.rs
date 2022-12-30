mod post_generator;
mod settings;
mod page_generator;

use tonic::{transport::Server, Request, Response, Status};

use post_generation::post_service_server::{PostService, PostServiceServer};
use post_generation::{Empty, PostGeneratingReply, PostRequest };
use crate::page_generation::page_service_server::{PageService, PageServiceServer};
use page_generation::{PageRequest, PageGeneratingReply};

use crate::post_generator::{generate_post, regenerate_all, regenerate_assets, is_generating};

pub mod post_generation {
    tonic::include_proto!("post_generation"); // The string specified here must match the proto package name
}

pub mod page_generation {
    tonic::include_proto!("page_generation"); // The string specified here must match the proto package name
}

#[derive(Debug, Default)]
pub struct PostServiceGreeter {}

#[tonic::async_trait]
impl PostService for PostServiceGreeter {
    async fn generate_post(
        &self,
        request: Request<PostRequest>,
    ) -> Result<Response<PostGeneratingReply>, Status> {
        println!("Got a request: {:?}", request);

        let reply = PostGeneratingReply {
            generating: generate_post(request.into_inner().uuid)
        };

        Ok(Response::new(reply))
    }

    async fn regenerate_all(&self, _request: Request<Empty>) -> Result<Response<PostGeneratingReply>, Status> {
        let reply = PostGeneratingReply {
            generating: regenerate_all()
        };
        Ok(Response::new(reply))
    }

    async fn regenerate_assets(&self, _request: Request<Empty>) -> Result<Response<Empty>, Status> {
        regenerate_assets();
        Ok(Response::new(Empty {}))
    }

    async fn is_generating(&self, _request: Request<Empty>) -> Result<Response<PostGeneratingReply>, Status> {
        let reply = PostGeneratingReply {
            generating: is_generating()
        };
        Ok(Response::new(reply))
    }
}

#[derive(Debug, Default)]
pub struct PageServiceGreeter {}

#[tonic::async_trait]
impl PageService for PageServiceGreeter {
    async fn generate_page(&self, request: Request<PageRequest>) -> Result<Response<PageGeneratingReply>, Status> {
        todo!()
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::1]:50051".parse()?;
    let post_greeter = PostServiceGreeter::default();
    let page_greeter = PageServiceGreeter::default();

    Server::builder()
        .add_service(PostServiceServer::new(post_greeter))
        .add_service(PageServiceServer::new(page_greeter))
        .serve(addr)
        .await?;

    Ok(())
}
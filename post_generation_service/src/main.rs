mod post_generator;
mod settings;
mod page_generator;
mod greeters;

use pgs_common;

use tonic::{transport::Server, Request, Response, Status};

use post_generation::post_service_server::{PostService, PostServiceServer};
use post_generation::{Empty, PostGeneratingReply, PostRequest };
use crate::page_generation::page_service_server::{PageService, PageServiceServer};
use page_generation::{PageRequest, PageGeneratingReply};
use crate::greeters::page_service_greeter::PageServiceGreeter;
use crate::greeters::post_service_greeter::PostServiceGreeter;

use crate::post_generator::{generate_post, regenerate_all, regenerate_assets, is_generating};

pub mod post_generation {
    tonic::include_proto!("post_generation"); // The string specified here must match the proto package name
}

pub mod page_generation {
    tonic::include_proto!("page_generation"); // The string specified here must match the proto package name
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
mod settings;
mod page_generator;
mod greeters;
mod post;

use std::net::ToSocketAddrs;
use pgs_common;

extern crate fs_extra;

use tonic::{transport::Server, Request, Response, Status};

use post_generation::post_service_server::{PostService, PostServiceServer};
use post_generation::{Empty, PostGeneratingReply, PostRequest };
use crate::page_generation::page_service_server::{PageService, PageServiceServer};
use page_generation::{PageRequest, PageGeneratingReply};
use sloth_config_lib::get_config;
use crate::greeters::page_service_greeter::PageServiceGreeter;
use crate::greeters::post_service_greeter::PostServiceGreeter;

pub mod post_generation {
    tonic::include_proto!("post_generation"); // The string specified here must match the proto package name
}

pub mod page_generation {
    tonic::include_proto!("page_generation"); // The string specified here must match the proto package name
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let conf_result = get_config();
    if conf_result.is_ok() {
        let config = conf_result.unwrap();
        let server_details = format!("{}:{}", config.post_generation_service.url, config.post_generation_service.port);
        let server: Vec<_> = server_details
            .to_socket_addrs()
            .expect("Unable to resolve domain")
            .collect();
        let post_greeter = PostServiceGreeter::default();
        let page_greeter = PageServiceGreeter::default();

        Server::builder()
            .add_service(PostServiceServer::new(post_greeter))
            .add_service(PageServiceServer::new(page_greeter))
            .serve(server[0])
            .await?;
    } else {
        println!("{:?}", conf_result);
        println!("beep");
    }
    Ok(())
}
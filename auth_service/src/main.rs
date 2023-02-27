#![feature(addr_parse_ascii)]

mod greeters;
mod authentication;

use std::net::{SocketAddr, ToSocketAddrs};
use tonic::{transport::Server, Request, Response, Status};
use sloth_config_lib::get_config;
use crate::greeters::auth_service_greeter;
use crate::greeters::auth_service_greeter::AuthServiceGreeter;
use crate::auth_service::auth_service_server::AuthServiceServer;

pub mod auth_service {
    tonic::include_proto!("auth_service"); // The string specified here must match the proto package name
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let conf = get_config();
    println!("{:?}", conf);
    if let Ok(config) = conf {
        let server_details = format!("{}:{}", config.auth_service.url, config.auth_service.port);
        let server: Vec<_> = server_details
            .to_socket_addrs()
            .expect("Unable to resolve domain")
            .collect();

        let auth_greeter = AuthServiceGreeter::default();

        println!("{:?}", server[0]);

        if server.len() > 0 {
            Server::builder()
                .add_service(AuthServiceServer::new(auth_greeter))
                .serve(server[0])
                .await?;
        }
    } else {
        println!("huh?")
    }

    Ok(())
}
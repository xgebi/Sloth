use std::time::Duration;
use post_generation::post_service_client::{PostServiceClient};
use post_generation::{ MultiplePostRequest };

pub mod post_generation {
    tonic::include_proto!("post_generation"); // The string specified here must match the proto package name
}

#[tokio::main]
async fn main() {
    println!("Hello!");
    // let mut client = PostServiceClient::connect("http://[::1]:50051").await?;
    //
    // // 1. fetch scheduled and ready to be published posts
    //
    // let request = tonic::Request::new(MultiplePostRequest {
    //     uuid: Vec::new()
    // });

    // 2. call post_generation_service
    // let response = client.say_hello(request).await?;
}

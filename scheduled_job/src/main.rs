use std::env;
use std::path::Path;
use std::time::Duration;
use confy::ConfyError;
use post_generation::post_service_client::{PostServiceClient};
use post_generation::{ MultiplePostRequest };
use sloth_config_lib::SlothConfig;

pub mod post_generation {
    tonic::include_proto!("post_generation"); // The string specified here must match the proto package name
}

#[tokio::main]
async fn main() {
    println!("Hello!");
    let config_file = env::var("SLOTH_CONFIG").ok();
    if let Some(file_path) = config_file {
        println!("{:?}", file_path);
        let path = Path::new(&file_path).to_owned();
        if path.exists() {
            println!("a");
            let config: Result<SlothConfig, ConfyError> = confy::load_path(Path::new(&file_path));
            println!("{:?}", config);
        }
        println!("b");
    }
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

use deadpool_postgres::tokio_postgres::connect;
use crate::post_generation::post_service_server::PostService;
use tonic::{transport::Server, Request, Response, Status};
use crate::post::files::copy_assets;
use crate::post::generator::{generate_post, is_generating, regenerate_all, regenerate_assets};
use crate::post_generation::{Empty, MultiplePostRequest, PostGeneratingReply, PostRequest};

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

    async fn generate_posts(&self, request: Request<MultiplePostRequest>) -> Result<Response<PostGeneratingReply>, Status> {
        todo!()
    }

    async fn regenerate_all(&self, _request: Request<Empty>) -> Result<Response<PostGeneratingReply>, Status> {
        let reply = PostGeneratingReply {
            generating: regenerate_all()
        };
        Ok(Response::new(reply))
    }

    async fn regenerate_assets(&self, _request: Request<Empty>) -> Result<Response<Empty>, Status> {
        copy_assets();
        Ok(Response::new(Empty {}))
    }

    async fn is_generating(&self, _request: Request<Empty>) -> Result<Response<PostGeneratingReply>, Status> {
        let reply = PostGeneratingReply {
            generating: is_generating()
        };
        Ok(Response::new(reply))
    }
}
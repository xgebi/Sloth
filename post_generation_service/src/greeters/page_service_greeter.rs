use tonic::{transport::Server, Request, Response, Status};
use crate::page_generation::page_service_server::PageService;
use crate::page_generation::{PageGeneratingReply, PageRequest};

#[derive(Debug, Default)]
pub struct PageServiceGreeter {}

#[tonic::async_trait]
impl PageService for PageServiceGreeter {
    async fn generate_page(&self, request: Request<PageRequest>) -> Result<Response<PageGeneratingReply>, Status> {
        todo!()
    }
}
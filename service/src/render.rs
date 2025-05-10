use std::collections::HashMap;
use std::fs::{File, exists};
use std::io::Read;
use actix_web::{web, HttpResponse, Error};
use serde::Deserialize;
use interpreters::{scan_toes, compile_toes};

#[derive(Clone, Deserialize, Debug)]
pub(crate) struct Page {
    pub(crate) config: HashMap<String, String>,

}

pub(crate) async fn render(item: web::Json<Page>) -> Result<HttpResponse, Error> {
    println!("{:?}", item);
    let page_data = item.into_inner();
    // fetch the template
    let template_path = page_data.config.get("template_path");
    let mut result = String::new();
    if template_path.is_some() && exists(template_path.clone().unwrap()).is_ok() {
        let mut file = File::open(template_path.unwrap())?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        println!("{:?}", contents);
        let result_node = scan_toes(contents);
        let compiled_node = compile_toes(result_node, VariableScope::create(), page_data.config)
    }
    Ok(HttpResponse::Ok().body(result))
}
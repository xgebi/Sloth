use std::collections::HashMap;
use std::fs::{File, exists};
use std::io::Read;
use actix_web::{web, HttpResponse, Error};
use serde::Deserialize;
use interpreters::{scan_toes, compile_toes, VariableScope, DataType};

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
        // load file
        let mut file = File::open(template_path.unwrap())?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        
        // parse XML
        let result_node = scan_toes(contents);
        
        let mut config: HashMap<String, DataType> = HashMap::new();
        for (key, value) in page_data.config {
            config.insert(key.clone(), DataType::from(value.clone()));
        }
        
        // process tree
        let compiled_node = compile_toes(result_node, VariableScope::create(), config);
    }
    Ok(HttpResponse::Ok().body(result))
}
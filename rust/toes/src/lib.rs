mod parser;
mod compiler;
mod node;
mod generator;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple};
use crate::parser::{parse_toes, Hooks};
use crate::node::ToeNode;
use atree::Arena;
use std::error::Error;
use std::io::Write;
use postgres::{Client, NoTls};

#[pyfunction]
fn parse_markdown_to_html(template: String) -> String {
    println!("Hello");
    String::new()
}

#[pyfunction]
fn generate_post(connection: &PyDict, mut working_directory_path: String, uuid: String) {
    if lock_generation(working_directory_path) < 0 {
        return;
    }
    if let Ok(mut conn) = created_connection(connection) {
        conn;
    }
}

#[pyfunction]
fn generate_post_type(connection: &PyDict, mut working_directory_path: String, uuid: String) {
    if lock_generation(working_directory_path) < 0 {
        return;
    }
    if let Ok(mut conn) = created_connection(connection) {
        conn;
    }
}

#[pyfunction]
fn generate_all(connection: &PyDict, mut working_directory_path: String) {
    if lock_generation(working_directory_path) < 0 {
        return;
    }
    if let Ok(mut conn) = created_connection(connection) {
        conn;
    }
}

fn lock_generation(mut working_directory_path: String) -> i8 {
    working_directory_path.push_str("generating.lock");
    if let b = std::path::Path::new(&working_directory_path).exists() {
        return -1;
    }

    let mut file = std::fs::File::create(&working_directory_path).expect("create failed");
    match file.write("generation locked".as_bytes()) {
        Ok(n) => println!("Lock successful"),
        Err(e) => {
            println!("Lock unsuccessful");
            return -1;
        }
    }
    return 1
}

fn created_connection(connection: &PyDict) -> Result<Client, postgres::Error> {
    let mut client = Client::connect("host=localhost user=postgres", NoTls)?;
    Ok(client)
}

// #[pyfunction]
// fn rust_render_toe_from_path<'a>(path: String, dummy: &PyDict) {
//     // println!("{:?}", dummy.get_item("name").unwrap());
//     // println!("{:?}", dummy);
//     println!("{:?}", dummy.get_item("hooks").unwrap());
//     // .extract::<Hooks>()
//     // match dummy.get_item("hooks").unwrap().extract::<Hooks>() {
//     //     Ok(v) => println!("{:?}", v),
//     //     Err(e) => println!("{:?}", e),
//     // }
// }

#[pymodule]
fn toes(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_markdown_to_html, m)?)?;
    m.add_function(wrap_pyfunction!(generate_post, m)?)?;
    m.add_function(wrap_pyfunction!(generate_post_type, m)?)?;
    m.add_function(wrap_pyfunction!(generate_all, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

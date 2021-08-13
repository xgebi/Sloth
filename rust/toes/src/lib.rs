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
use crate::generator::prepare_single_post;

#[pyfunction]
fn parse_markdown_to_html(template: String) -> String {
    println!("Hello");
    String::new()
}

#[pyfunction]
fn generate_post(
    connection_dict: &PyDict,
    working_directory_path: String,
    post: &PyDict,
    theme_path: String,
    output_path: String,
    clean_taxonomy: Option<bool>
) {
    if lock_generation(working_directory_path) < 0 {
        return;
    }
    if let Ok(mut conn) = created_connection(connection_dict) {
        prepare_single_post(conn, post, theme_path, output_path);
    }
}

#[pyfunction]
fn generate_post_type(connection_dict: &PyDict, mut working_directory_path: String, uuid: String) {
    if lock_generation(working_directory_path) < 0 {
        return;
    }
    if let Ok(mut conn) = created_connection(connection_dict) {
        conn;
    }
}

#[pyfunction]
fn generate_all(connection_dict: &PyDict, mut working_directory_path: String) {
    if lock_generation(working_directory_path) < 0 {
        return;
    }
    if let Ok(mut conn) = created_connection(connection_dict) {
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

fn created_connection(connection_dict: &PyDict) -> Result<Client, postgres::Error> {
    let dbname: &str = connection_dict.get_item("DATABASE_NAME").unwrap().extract::<&str>().unwrap();
    let dbuser: &str = connection_dict.get_item("DATABASE_USER").unwrap().extract::<&str>().unwrap();
    let dbpass: &str = connection_dict.get_item("DATABASE_PASSWORD").unwrap().extract::<&str>().unwrap();
    let dbhost: &str = connection_dict.get_item("DATABASE_URL").unwrap().extract::<&str>().unwrap();
    let dbport: &str = connection_dict.get_item("DATABASE_PORT").unwrap().extract::<&str>().unwrap();
    // host=/var/run/postgresql,localhost port=1234 user=postgres password='password with spaces'
    let connection_string: String = format!("host={} port={} user={} password='{}' dbname={}",
                                            dbhost, dbport, dbuser, dbpass, dbname);

    let mut client = Client::connect(&*connection_string, NoTls)?;
    Ok(client)
}

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

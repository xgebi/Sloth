#![cfg_attr(test, feature(proc_macro_hygiene))]

#[cfg(test)]
use mocktopus::macros::mockable;

mod markdown;
mod toes;
mod post;
mod repositories;

use std::io::Write;
use std::error::Error;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple, PyList};
use postgres::{Client, NoTls};
use crate::post::post::prepare_post;

#[pymodule]
fn toes(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_markdown_to_html, m)?)?;
    m.add_function(wrap_pyfunction!(generate_post, m)?)?;
    // m.add_function(wrap_pyfunction!(generate_post_type, m)?)?;
    // m.add_function(wrap_pyfunction!(generate_all, m)?)?;
    Ok(())
}

#[pyfunction]
fn parse_markdown_to_html(template: String) -> String {
    String::new()
}

#[pyfunction]
fn generate_post(
    connection_dict: &PyDict,
    working_directory_path: String,
    python_post: &PyDict,
    theme_path: String,
    output_path: String,
    clean_taxonomy: Option<Vec<String>>
) {
    println!("{}", working_directory_path);
    if lock_generation(&working_directory_path) < 0 {
        println!("lock failed");
        return;
    }

    let post_data = post::post_struct::Post::new(python_post);

    if let Ok(mut conn) = created_connection(connection_dict) {
        prepare_post(conn, post_data);
    }

    unlock_generation(&working_directory_path);
}

fn lock_generation(mut working_directory_path: &String) -> i8 {
    let file_path = std::path::Path::new(working_directory_path).join("generating.lock");
    if file_path.exists() {
        println!("lock exists, {}", file_path.to_str().unwrap());
        return -1;
    }

    let mut file = std::fs::File::create(file_path).expect("create failed");
    match file.write("generation locked".as_bytes()) {
        Ok(_) => println!("Lock successful"),
        Err(e) => {
            println!("Lock unsuccessful");
            return -1;
        }
    }
    return 1
}

fn unlock_generation(mut working_directory_path: &String) {
    let file_path = std::path::Path::new(&working_directory_path).join("generating.lock");
    if file_path.exists() {
        match std::fs::remove_file(file_path) {
            Ok(_) => println!("generation unlocked"),
            Err(e) => println!("{:?}", e)
        }
    }
}

fn created_connection(connection_dict: &PyDict) -> Result<Client, postgres::Error> {
    let dbname: &str = connection_dict.get_item("dbname").unwrap().extract::<&str>().unwrap();
    let dbuser: &str = connection_dict.get_item("user").unwrap().extract::<&str>().unwrap();
    let dbpass: &str = connection_dict.get_item("password").unwrap().extract::<&str>().unwrap();
    let dbhost: &str = connection_dict.get_item("host").unwrap().extract::<&str>().unwrap();
    let dbport: &str = connection_dict.get_item("port").unwrap().extract::<&str>().unwrap();
    // host=/var/run/postgresql,localhost port=1234 user=postgres password='password with spaces'
    let connection_string: String = format!("host={} port={} user={} password='{}' dbname={}",
                                            dbhost, dbport, dbuser, dbpass, dbname);

    let mut client = Client::connect(&*connection_string, NoTls)?;
    Ok(client)
}
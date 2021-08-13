mod parser;
mod compiler;
mod node;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple};
use crate::parser::{parse_toes, Hooks};
use crate::node::ToeNode;
use atree::Arena;
use std::error::Error;

#[derive(Clone)]
struct Dummy {
    name: String
}

#[pyfunction]
fn parse_markdown_to_html(template: String) -> String {
    println!("Hello");
    String::new()
}

#[pyfunction]
fn rust_render_toe_from_string() {

}

#[pyfunction]
fn rust_render_toe_from_path<'a>(path: String, dummy: &PyDict) {
    // println!("{:?}", dummy.get_item("name").unwrap());
    // println!("{:?}", dummy);
    println!("{:?}", dummy.get_item("hooks").unwrap());
    // .extract::<Hooks>()
    // match dummy.get_item("hooks").unwrap().extract::<Hooks>() {
    //     Ok(v) => println!("{:?}", v),
    //     Err(e) => println!("{:?}", e),
    // }
}

#[pymodule]
fn toes(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_markdown_to_html, m)?)?;
    m.add_function(wrap_pyfunction!(rust_render_toe_from_string, m)?)?;
    m.add_function(wrap_pyfunction!(rust_render_toe_from_path, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

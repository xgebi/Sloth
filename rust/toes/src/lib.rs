mod parser;
mod compiler;
mod node;

use pyo3::prelude::*;
use crate::parser::parse_toes;
use crate::node::ToeNode;
use atree::Arena;
use std::error::Error;

#[pyfunction]
fn parse_markdown_to_html(template: String) -> String {
    println!("Hello");
    String::new()
}

#[pymodule]
fn toes(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_markdown_to_html, m)?)?;
    Ok(())
}

/// This module is implemented in Rust.
// #[pymodule]
// fn my_extension(py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(double, m)?)?;
//     Ok(())
// }

pub fn parse_toe_template(template: String) -> Arena<ToeNode> {
    parse_toes(template)
}

pub fn parse_toe_file(path: String) -> Arena<ToeNode> {
    parse_toes(String::new())
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

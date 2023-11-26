#![feature(in_band_lifetimes)]
#![cfg_attr(test, feature(proc_macro_hygiene))]

use std::io::Write;
use std::error::Error;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple, PyList, PyString};
use postgres::{Client, NoTls};
use crate::markdown::mdparser::MarkdownParser;

#[pymodule]
fn toes(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_markdown_to_html, m)?)?;
    m.add_function(wrap_pyfunction!(parse_toe_to_html_file, m)?)?;
    Ok(())
}

#[pyfunction]
fn parse_markdown_to_html(template: PyString) -> String {
    let parser = MarkdownParser::new(template.to_string());
    parser.get_html_code()
}

#[pyfunction]
fn parse_toe_to_html_file(
    working_directory_path: PyString,
    python_post: PyDict,
    theme_path: PyString,
    output_path: PyString,
    settings: PyDict,
    menus: PyDict,
) {
    todo!()
}


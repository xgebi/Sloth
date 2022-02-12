#![feature(in_band_lifetimes)]
#![cfg_attr(test, feature(proc_macro_hygiene))]

mod markdown;
mod toes;
mod post;
mod repositories;
mod common;

use std::io::Write;
use std::error::Error;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple, PyList};
use postgres::{Client, NoTls};
use crate::post::post::prepare_post;

#[pymodule]
fn toes(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_markdown_to_html, m)?)?;
    m.add_function(wrap_pyfunction!(parse_toe_to_html_file, m)?)?;
    Ok(())
}

#[pyfunction]
fn parse_markdown_to_html(template: String) -> String {
    String::new()
}

#[pyfunction]
fn parse_toe_to_html_file() {
    todo!()
}


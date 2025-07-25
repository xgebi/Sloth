use std::collections::HashMap;
use std::fmt::{Display, Formatter};
use pyo3::prelude::*;
use crate::data_type::DataType;
use crate::runners::scan_toes;

mod runners;
mod node;
mod data_type;
mod node_type;
mod conditions;
mod variable_scope;
mod toe_commands;
mod slothmark;
mod patterns;

#[derive(Debug, Clone)]
#[pyclass]
pub struct Footnote {
    text: String,
    index: isize,
}

impl Display for Footnote {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", format!("<li>{}</li>", self.text))
    }
}

#[pyfunction]
pub(crate) fn display_vec_footnote(mut v: Vec<Footnote>) -> String {
    if v.is_empty() {
        return String::new();
    }
    v.sort_by(|a, b| a.index.cmp(&b.index));
    let mut res = String::from("<h2>Footnotes</h2><ol>");
    for footnote in v {
        res = format!("{}<li>{}</li>", res, footnote.text);
    }

    format!("{}</ol>", res)
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct SlothMarkResult {
    pub text: String,
    pub footnotes: Vec<Footnote>
}

#[pyfunction]
fn render_slothmark(input: String) -> (String, Vec<Footnote>) {
    runners::render_markup(input)
}

#[pyfunction]
fn render_toe(input: String, data: HashMap<String, String>) -> PyResult<String> {
    let result = scan_toes(input);
    Ok(String::new())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_generators(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render_slothmark, m)?)?;
    m.add_function(wrap_pyfunction!(display_vec_footnote, m)?)?;
    m.add_class::<SlothMarkResult>()?;
    m.add_class::<Footnote>()?;
    Ok(())
}

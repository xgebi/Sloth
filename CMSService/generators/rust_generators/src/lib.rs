use pyo3::prelude::*;

mod runners;
mod node;
mod data_type;
mod node_type;
mod conditions;
mod variable_scope;
mod toe_commands;
mod slothmark;
mod patterns;

pub struct Footnote {
    text: String,
    index: isize,
} 

#[pyclass]
pub struct SlothMarkResult {
    pub text: String,
    pub footnotes: Vec<Footnote>
}

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn render_slothmark(input: String) -> String {
    runners::render_markup(input)
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_generators(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(render_slothmark, m)?)?;
    m.add_class::<SlothMarkResult>()?;
    Ok(())
}

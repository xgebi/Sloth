use pyo3::prelude::*;
use interpreters;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn render_slothmark(input: String) -> String {
    interpreters::render_markup(input)
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_generators(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(render_slothmark, m)?)?;
    Ok(())
}

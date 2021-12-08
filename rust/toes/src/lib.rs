mod markdown;
mod toes;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple, PyList};

#[pyfunction]
fn parse_markdown_to_html(template: String) -> String {
    String::new()
}

#[pyfunction]
fn generate_post(
    // connection_dict: &PyDict,
    // working_directory_path: String,
    // post: &PyDict,
    // theme_path: String,
    // output_path: String,
    // clean_taxonomy: Option<Vec<String>>
) {
    toes::parser::mocked_function(2);
}

#[cfg(test)]
mod tests {
    use crate::generate_post;
    use crate::toes;
    use mocktopus::mocking::*;

    #[test]
    fn test_generate_post() {
        let ctx = toes::parser::mocked_function.mock_safe(|x| {
            assert_eq!(2, x);
            MockResult::Return(x)
        });

        generate_post();
    }
}
use std::fs;
use std::path::Path;
use pgs_common::node::Node;
use crate::compiler::compile_node_tree;
use crate::parser::parse_toe;

mod compiler;
mod parser;
mod variable_scope;
mod conditions;

pub fn render_page_from_string(s: String) -> String {
    let parsed_nodes = parse_toe(s);
    match parsed_nodes {
        Ok(n) => {
            let compiled = compile_node_tree(n);
            compiled.to_string()
        }
        Err(_) => { panic!("String couldn't be parsed")}
    }
}

pub fn render_page_from_path(path: String) -> String {
    let file_path = Path::new(&path);
    if file_path.exists() && file_path.is_file() {
        let contents = fs::read_to_string(file_path);
        if contents.is_ok() {
            return render_page_from_string(contents.unwrap());
        }
    }
    panic!("File couldn't be parsed")
}

// #[cfg(test)]
// mod tests {
//     use super::*;
//
//     #[test]
//     fn it_works() {
//         let result = add(2, 2);
//         assert_eq!(result, 4);
//     }
// }

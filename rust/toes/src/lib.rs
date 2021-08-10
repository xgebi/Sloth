mod parser;
mod compiler;
mod node;

use crate::parser::parse_toes;
use crate::node::ToeNode;
use atree::Arena;
use std::error::Error;

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

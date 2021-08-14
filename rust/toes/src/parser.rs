use atree::Arena;
use atree::Token;
use std::error::Error;
use crate::node::ToeNode;
use pyo3::prelude::*;

enum States {
    NewPage,
    ReadNodeName,
    LookingForAttribute,
    LookingForChildNodes,
    InsideScript,
}

#[derive(Clone, Debug, FromPyObject)]
pub(crate) struct Hook {
    #[pyo3(item("content"))]
    content: String,
    #[pyo3(item("condition"))]
    condition: String
}

#[derive(Clone, Debug, FromPyObject)]
pub(crate) struct Hooks {
    #[pyo3(item("footer"))]
    footer: Vec<Hook>,
    #[pyo3(item("head"))]
    head: Vec<Hook>
}

struct XmlParsingInfo<'a> {
    i: u32,
    state: States,
    current_node: &'a Token,
    root_node: &'a Token,
}

pub(crate) fn parse_toes(mut template: String) -> Arena<ToeNode> {
    let mut a: Arena<ToeNode> = Arena::new();
    if template.chars().count() == 0 {
        return a;
    }

    // let s = String::from("hello world");
    //
    // let hello = &s[0..5];
    // let world = &s[6..11];
    // let first_and_last = [&v[..3], &v[l - 3..]].concat();

    a
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
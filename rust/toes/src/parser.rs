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
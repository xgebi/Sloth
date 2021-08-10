use atree::Arena;
use atree::Token;
use std::error::Error;
use crate::node::ToeNode;

enum States {
    new_page,
    read_node_name,
    looking_for_attribute,
    looking_for_child_nodes,
    inside_script,
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

    a
}
use std::error::Error;
use crate::node::{ToeNode, ToeTreeTop};
use pyo3::prelude::*;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;

enum States {
    NewPage,
    ReadNodeName,
    LookingForAttribute,
    LookingForChildNodes,
    InsideScript,
}

struct XmlParsingInfo {
    i: u32,
    state: States,
    current_node: Rc<ToeNode>,
    root_node: Rc<ToeNode>,
}

pub(crate) fn parse_toes(mut template: String) -> ToeTreeTop {
    let mut res = ToeTreeTop {
        children: Vec::new(),
    };
    if template.chars().count() == 0 {
        return res;
    }

    // let s = String::from("hello world");
    //
    // let hello = &s[0..5];
    // let world = &s[6..11];
    // let first_and_last = [&v[..3], &v[l - 3..]].concat();
    res
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
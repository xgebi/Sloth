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
    current_node: Option<Rc<ToeNode>>,
    root_node: Rc<ToeTreeTop>,
}

impl XmlParsingInfo {
    fn move_index(&mut self, step: Option<u32>) {
        match step {
            None => {
                self.i += 1;
            }
            Some(s) => {
                self.i += s;
            }
        }
    }
}

pub(crate) fn parse_toes(mut template: String) -> Rc<ToeTreeTop> {
    let mut res = ToeTreeTop {
        children: Vec::new(),
    };
    if template.len() == 0 {
        return Rc::new(res);
    }
    let iterable_template = template.graphemes(true).collect::<Vec<&str>>();
    let mut parsing_info = XmlParsingInfo {
        i: 0,
        state: States::NewPage,
        current_node: None,
        root_node: Rc::new(res)
    };
    loop {
        match iterable_template[parsing_info.i] {
            "<" => {
                parse_starting_tag_character(&iterable_template, &mut parsing_info)
            }
            ">" => {
                parse_ending_tag_character()
            }
            _ => {
                let ch: &str = iterable_template[parsing_info.i];
                if ch.trim().len() == 0 {
                    parsing_info.move_index(None);
                } else {

                }
            }
        }

        if parsing_info.i == iterable_template.len() as u32 {
            break;
        }
    }

    parsing_info.root_node
}

fn parse_starting_tag_character(template: &Vec<&str>, parsing_info: &mut XmlParsingInfo) {
    if template[parsing_info.i + 1] == " " {
        parsing_info.move_index(None);
    } else if parsing_info.state == States::NewPage {

    } else if parsing_info.state == States::LookingForChildNodes {

    } else {
        parsing_info.move_index(None);
    }
}

fn parse_ending_tag_character() {

}

#[cfg(test)]
mod tests {
    use crate::node::ToeTreeTop;
    use crate::toe_parser::{XmlParsingInfo, States, parse_starting_tag_character};
    use std::rc::Rc;

    #[test]
    fn test_index_move_by_one() {
        let mut res = ToeTreeTop {
            children: Vec::new(),
        };
        let mut parsing_info = XmlParsingInfo {
            i: 0,
            state: States::NewPage,
            current_node: None,
            root_node: Rc::new(res)
        };
        parsing_info.move_index(None);
        assert_eq!(parsing_info.i, 1);
    }

    #[test]
    fn test_index_move_by_two() {
        let mut res = ToeTreeTop {
            children: Vec::new(),
        };
        let mut parsing_info = XmlParsingInfo {
            i: 0,
            state: States::NewPage,
            current_node: None,
            root_node: Rc::new(res)
        };
        parsing_info.move_index(Some(2));
        assert_eq!(parsing_info.i, 2);
    }

    #[test]
    fn test_parse_starting_tag_character() {
        // parse_starting_tag_character()
    }
}
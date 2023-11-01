#[derive(PartialEq, Eq, Debug, Copy, Clone)]
pub enum JunctionType {
    None,
    And,
    Or
}

#[derive(Clone, Debug)]
pub(crate) struct ConditionNode {
    contents: String,
    junction: JunctionType,
    children: Vec<ConditionNode>,
}

pub(crate) fn process_condition(graphemes: Vec<&str>) -> bool {

    true
}

fn parse_condition_tree(graphemes: Vec<&str>) -> ConditionNode {
    let mut node = ConditionNode {
        contents: String::new(),
        junction: JunctionType::None,
        children: Vec::new(),
    };

    let mut parenthesis_counter = 0;
    let mut used_quotes = "";
    let mut start: usize = 0;
    let mut end: usize = 0;
    while end < graphemes.len() {
        match graphemes[end] {
            _ => {
                end += 1;
            }
        }

        if end == graphemes.len() {
            node.contents = graphemes[start..end].join("");
        }
    }

    node
}

#[cfg(test)]
mod node_tests {
    use unicode_segmentation::UnicodeSegmentation;
    use super::*;

    #[test]
    fn parse_boolean_to_node() {
        let cond = "true".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("true"));
    }

    #[test]
    fn parse_variable_to_node() {
        let cond = "my_var".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("my_var"));
    }

    #[test]
    fn parse_less_than_variable_to_node() {

    }
}

#[cfg(test)]
mod parsing_tests {
    use unicode_segmentation::UnicodeSegmentation;
    use crate::conditions::{parse_condition_tree, process_condition};

    #[test]
    fn parse_number() {
        let cond = "1".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.contents, "1");
    }
}
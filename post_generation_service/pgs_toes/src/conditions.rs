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
    let mut i: usize = 0;
    while i < graphemes.len() {
        match graphemes[i] {
            "(" => {
                parenthesis_counter += 1;
                i += 1;
            }
            ")" => {
                parenthesis_counter -= 1;
                if parenthesis_counter < 0 && used_quotes.len() == 0 {
                    panic!("Invalid condition encountered");
                }
                i += 1;
            }
            "\"" => {
                if used_quotes.len() == 0 {
                    if i == 0 || (i - 1 >= 0 && graphemes[i - 1] != "\"") {
                        used_quotes = "\"";
                    }
                } else if i - 1 >= 0 && graphemes[i - 1] == "\"" {
                    used_quotes = "";
                }
                i += 1;
            }
            " " => {
                let mut j = i + 1;
                while j < graphemes.len() {
                    if graphemes[j] == " " {
                        j += 1;
                    } else {
                        if j + 1 < graphemes.len() && graphemes[j] == "o" && graphemes[j+1] == "r" {
                            // There might be bugs in this logic, I need to think it through more
                            if j + 2 == graphemes.len() {
                                panic!("Unfinished condition encountered");
                            } else if graphemes[j + 3] == " " || graphemes[j + 3] == ")" {
                                node.junction = JunctionType::Or;
                                // get a condition and parse it
                            }
                            j += 2;
                        } else if j + 2 < graphemes.len() && graphemes[j] == "a" && graphemes[j+1] == "n" && graphemes[j+2] == "d" {
                            // There might be bugs in this logic, I need to think it through more
                            if j + 3 == graphemes.len() {
                                panic!("Unfinished condition encountered");
                            } else if graphemes[j + 3] == " " || graphemes[j + 3] == ")" {
                                node.junction = JunctionType::And;
                                // get a condition and parse it
                            }
                            j += 3;
                        }
                    }
                }
                i += (j - i);
            }
            _ => {
                i += 1;
            }
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
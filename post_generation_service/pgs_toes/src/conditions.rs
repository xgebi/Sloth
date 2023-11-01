#[derive(PartialEq, Eq, Debug, Copy, Clone)]
pub enum JunctionType {
    None,
    And,
    Or
}

#[derive(Clone, Debug)]
pub(crate) struct ConditionNode {
    contents: String,
    junctions: Vec<JunctionType>,
    children: Vec<ConditionNode>,
}

pub(crate) fn process_condition(graphemes: Vec<&str>) -> bool {

    true
}

fn parse_condition_tree(graphemes: Vec<&str>) -> ConditionNode {
    let mut node = ConditionNode {
        contents: String::new(),
        junctions: Vec::new(),
        children: Vec::new(),
    };

    let mut inside_the_quotes = false;
    let mut used_quotes = "";
    let mut parenthesis_counter: usize = 0;
    let mut start: usize = 0;
    let mut end: usize = 0;
    while end < graphemes.len() {
        match graphemes[end] {
            "o" => {
                if !inside_the_quotes && parenthesis_counter == 0 && end + 1 < graphemes.len() && graphemes[end + 1] == "r" {
                    if start == end {
                        panic!("And cannot be a variable or be at the start of the condition");
                    }
                    if end + 2 == graphemes.len() {
                        panic!("There has to be second part of the condition");
                    }

                    let new_node = parse_condition_tree(graphemes[start..end].to_vec());
                    node.junctions.push(JunctionType::Or);
                    node.children.push(new_node);
                    end += 2;
                    start = end;
                } else {
                    end += 1
                }
            }
            "a" => {
                if !inside_the_quotes && parenthesis_counter == 0 && end + 2 < graphemes.len() && graphemes[end + 1] == "n" && graphemes[end + 2] == "d" {
                    if start == end {
                        panic!("And cannot be a variable or be at the start of the condition");
                    }
                    if end + 3 == graphemes.len() {
                        panic!("There has to be second part of the condition");
                    }
                    let new_node = parse_condition_tree(graphemes[start..end].to_vec());
                    node.junctions.push(JunctionType::And);
                    node.children.push(new_node);
                    end += 3;
                    start = end;
                } else {
                    end += 1
                }
            }
            "(" => {
                if !inside_the_quotes {
                    parenthesis_counter += 1;
                }
                end += 1;
            }
            ")" => {
                if !inside_the_quotes {
                    parenthesis_counter -= 1;
                }
                end += 1;
            }
            "'" => {
                if !inside_the_quotes {
                    used_quotes = "'";
                    inside_the_quotes = true;
                } else {
                    if used_quotes == "'" {
                        inside_the_quotes = false;
                    }
                }
                end += 1;
            }
            "\\" => {
                end += 2;
            }
            _ => {
                end += 1;
            }
        }

        if end == graphemes.len() {
            if node.children.len() > 0 {
                node.children.push(parse_condition_tree(graphemes[start..end].to_vec()));
            } else {
                node.contents = graphemes[start..end].join("").trim().to_string();
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
    fn parse_string_to_node() {
        let cond = "'str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("'str'"));
    }

    #[test]
    fn parse_string_to_node_with_backlash() {
        let cond = "'\\\\str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("'\\\\str'"));
    }

    #[test]
    fn parse_string_to_node_with_backlash_single_quote() {
        let cond = "'\'str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("'\'str'"));
    }
    #[test]
    fn parse_string_to_node_with_backlash_double_quote() {
        let cond = "'\\\"str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("'\\\"str'"));
    }

    #[test]
    fn parse_string_to_node_double() {
        let cond = "\"str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("\"str\""));
    }

    #[test]
    fn parse_string_to_node_double_with_backlash() {
        let cond = "\"\\\\str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("\"\\\\str\""));

    }

    #[test]
    fn parse_string_to_node_double_with_backlash_single_quote() {
        let cond = "\"\'str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("\"\'str\""));
    }
    #[test]
    fn parse_string_to_node_double_with_backlash_double_quote() {
        let cond = "\"\"str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        assert_eq!(res.contents, String::from("\"\"str\""));
    }

    #[test]
    #[should_panic]
    fn should_panic_and_at_start() {
        let cond = "and test".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);
    }

    #[test]
    #[should_panic]
    fn should_panic_and_at_end() {
        let cond = "test and".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);
    }

    #[test]
    #[should_panic]
    fn should_panic_or_at_start() {
        let cond = "or test".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);
    }

    #[test]
    #[should_panic]
    fn should_panic_or_at_end() {
        let cond = "test or".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);
    }

    #[test]
    fn parse_and_to_node() {
        let cond = "my_var and not_my_var".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        println!("{:?}", res);
        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, "my_var");
        assert_eq!(res.children[1].contents, "not_my_var");
        assert_eq!(res.contents, String::from(""));
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::And);
    }

    #[test]
    fn parse_or_to_node() {
        let cond = "my_var or not_my_var".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        println!("{:?}", res);
        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, "my_var");
        assert_eq!(res.children[1].contents, "not_my_var");
        assert_eq!(res.contents, String::from(""));
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::Or);
    }
}
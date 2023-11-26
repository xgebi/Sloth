use std::cell::{BorrowError, Ref, RefCell};
use std::cmp::Ordering;
use std::ops::Deref;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;
use crate::variable_scope::VariableScope;

#[derive(Clone, Debug)]
pub(crate) struct Comparison {
    name: String,
    location: Option<usize>
}

impl Eq for Comparison {}

impl Ord for Comparison {
    fn cmp(&self, other: &Self) -> Ordering {
        self.location.unwrap().cmp(&other.location.unwrap())
    }
}

impl PartialOrd for Comparison {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Comparison {
    fn eq(&self, other: &Self) -> bool {
        self.location.unwrap() == other.location.unwrap()
    }
}

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

impl ConditionNode {
    pub fn compute(&self, vs: Rc<RefCell<VariableScope>>) -> bool {
        if self.contents.len() > 0 {
            if self.contents == String::from("true") {
                return true;
            }
            if self.contents == String::from("false") {
                return true;
            }
            // " gt ", " gte ", " lt ", " lte ", " eq ", " neq "
            let mut comp_vec = vec![];
            comp_vec.push(Comparison { location: self.contents.find(" gt "), name: String::from(" gt ") });
            comp_vec.push(Comparison { location: self.contents.find(" gte "), name: String::from(" gte ") });
            comp_vec.push(Comparison { location: self.contents.find(" lt "), name: String::from(" lt ") });
            comp_vec.push(Comparison { location: self.contents.find(" lte "), name: String::from(" lte ") });
            comp_vec.push(Comparison { location: self.contents.find(" eq "), name: String::from(" eq ") });
            comp_vec.push(Comparison { location: self.contents.find(" neq "), name: String::from(" neq ") });

            if comp_vec.len() > 0 {
                let mut comp_in_use = vec![];
                for comp in comp_vec {
                    if comp.location.is_some() {
                        comp_in_use.push(comp.clone());
                    }
                }
                comp_in_use.sort();
                for comp in comp_in_use {
                    if Self::is_in_quotes(self.contents.clone(), comp.name) {
                        let left: String = self.contents.clone().chars().take(comp.location.unwrap()).collect();
                        let right: String = self.contents.clone().chars().skip(comp.location.unwrap() + comp.name.len()).take(comp.location.unwrap()).collect();
                        match comp.name.as_str() {
                            " gt " => {}
                            " gte " => {}
                            " lt " => {}
                            " lte " => {}
                            " eq " => {}
                            " neq " => {}
                            _ => {
                                panic!("Something in comparisons went wrong")
                            }
                        }
                    }
                }
            }

            false
        } else if self.junctions.len() + 1 == self.children.len() {

            false
        } else {
            false
        }
    }

    fn is_in_quotes(s: String, comparison: String) -> bool {
        let single_quote_loc = s.find("'");
        let double_quote_loc = s.find("\"");
        let comparison_loc = s.find(comparison.as_str());
        if comparison_loc.is_some() && (single_quote_loc.is_some() || double_quote_loc.is_some())  {
            let chars = s.graphemes(true).collect::<Vec<&str>>();
            let mut idx = 0;
            let mut in_quote = false;
            let mut current_quote = String::new();
            while idx < comparison_loc.unwrap() {
                if chars[idx] == "'" || chars[idx] == "\"" {
                    if in_quote && (chars[idx] == current_quote && idx > 0 && chars[idx - 1] != "\"") {
                        in_quote = false;
                        current_quote = String::new();
                    } else {
                        in_quote = true;
                        current_quote = String::from(chars[idx]);
                    }
                }
                idx += 1;
            }
            return in_quote;
        }
        false
    }

    fn process_gt(s: String, vs: Rc<RefCell<VariableScope>>) -> bool {
        false
    }

    fn process_gte(s: String, vs: Rc<RefCell<VariableScope>>) -> bool {
        false
    }

    fn process_lt(s: String, vs: Rc<RefCell<VariableScope>>) -> bool {
        false
    }

    fn process_lte(s: String, vs: Rc<RefCell<VariableScope>>) -> bool {
        false
    }

    fn process_eq(s: String, vs: Rc<RefCell<VariableScope>>) -> bool {
        false
    }

    fn process_neq(s: String, vs: Rc<RefCell<VariableScope>>) -> bool {
        false
    }
}

pub(crate) fn process_condition(graphemes: Vec<&str>, variable_scope: Rc<RefCell<VariableScope>>) -> bool {
    let mut node = parse_condition_tree(graphemes);
    node.compute(variable_scope)
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

#[cfg(test)]
mod condition_resolving_tests {
    use std::cell::RefCell;
    use std::rc::Rc;
    use unicode_segmentation::UnicodeSegmentation;
    use super::*;

    #[test]
    fn resolve_true_boolean_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: "true".to_string(),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_false_boolean_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: "false".to_string(),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }
}
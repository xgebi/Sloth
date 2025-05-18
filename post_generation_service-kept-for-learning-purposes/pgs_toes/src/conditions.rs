use std::cell::{RefCell};
use std::cmp::Ordering;
use std::collections::HashMap;
use std::ops::Deref;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;
use crate::string_helpers::process_string_with_variables;
use crate::variable_scope::{VariableScope};
use pgs_common::value::Value;

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
pub(crate) enum ConditionContents {
    Variable(String),
    Boolean(bool),
    Nil,
    Number(f64),
    String(String),
    HashMap(HashMap<String, Rc<Value>>),
    Array(Vec<Rc<Value>>)
}

impl PartialEq for ConditionContents {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (ConditionContents::Boolean(a), ConditionContents::Boolean(b)) => a == b,
            (ConditionContents::Nil, ConditionContents::Nil) => true,
            (ConditionContents::Number(a), ConditionContents::Number(b)) => a == b,
            (ConditionContents::String(a), ConditionContents::String(b)) => a == b,
            (ConditionContents::Array(a), ConditionContents::Array(b)) => {
                if a.len() != b.len() {
                    return false;
                }
                for i in 0..a.len() {
                    if a[i] != b[i] {
                        return false;
                    }
                }
                true
            }
            (ConditionContents::HashMap(a), ConditionContents::HashMap(b)) => {
                if a.keys().len() != b.keys().len() {
                    return false;
                }
                for i in a.keys() {
                    if b.get(i).is_none() {
                        return false;
                    }
                }
                true
            }
            (ConditionContents::Variable(a), ConditionContents::Variable(b)) => a == b,
            _ => false,
        }
    }
}


#[derive(Clone, Debug)]
pub(crate) struct ConditionNode {
    contents: ConditionContents,
    junctions: Vec<JunctionType>,
    children: Vec<ConditionNode>,
}

impl ConditionNode {
    pub fn compute(&self, vs: Rc<RefCell<VariableScope>>) -> bool {
        if ConditionContents::Nil == self.contents && self.junctions.len() == 0 {
            return false;
        }

        if self.junctions.len() + 1 == self.children.len() {
            let mut result = false;
            let mut idx = 0;
            while idx < self.children.len() {
                if idx == 0 {
                    result = self.children[idx].compute_condition_content(Rc::clone(&vs)).unwrap_or(false);
                } else {
                    let temp = self.children[idx].compute_condition_content(Rc::clone(&vs)).unwrap_or(false);

                    match self.junctions[idx - 1] {
                        JunctionType::None => { panic!("Incorrect junction occurred") }
                        JunctionType::And => {
                            result = result && temp;
                            if !temp {
                                break;
                            }
                        }
                        JunctionType::Or => {
                            result = result || temp;
                        }
                    }
                }
                idx += 1;
            }
            return result;
        } else {
            return self.compute_condition_content(Rc::clone(&vs)).unwrap_or(false);
        }
        // } else if let ConditionContents::Boolean(val) = self.contents.clone() {
        //     return val;
        // } else if let ConditionContents::String(val) = self.contents.clone() {
        //     return val.len() > 0;
        // } else if let ConditionContents::Number(val) = self.contents.clone() {
        //     return val > 0.0;
        // }
        false
    }

    fn compute_condition_content(&self, vs: Rc<RefCell<VariableScope>>) -> Option<bool> {
        if self.contents == ConditionContents::Boolean(true) {
            return Some(true);
        }
        if self.contents == ConditionContents::Boolean(false) {
            return Some(false);
        }
        // " gt ", " gte ", " lt ", " lte ", " eq ", " neq "
        let mut comp_vec = vec![];
        if let ConditionContents::String(content) = self.contents.clone() {
            comp_vec.push(Comparison { location: content.find(" gt "), name: String::from(" gt ") });
            comp_vec.push(Comparison { location: content.find(" gte "), name: String::from(" gte ") });
            comp_vec.push(Comparison { location: content.find(" lt "), name: String::from(" lt ") });
            comp_vec.push(Comparison { location: content.find(" lte "), name: String::from(" lte ") });
            comp_vec.push(Comparison { location: content.find(" eq "), name: String::from(" eq ") });
            comp_vec.push(Comparison { location: content.find(" neq "), name: String::from(" neq ") });

            if comp_vec.len() > 0 {
                let mut comp_in_use = vec![];
                for comp in comp_vec {
                    if comp.location.is_some() {
                        comp_in_use.push(comp.clone());
                    }
                }
                if comp_in_use.is_empty() {
                    let l = vs.try_borrow();
                    match l {
                        Ok(ref_vs) => {
                            let k = ref_vs.clone();
                            match self.contents.clone() {
                                ConditionContents::Variable(v) => {
                                    if ref_vs.clone().variable_exists(&v) {
                                        let v = ref_vs.clone().find_variable(v).unwrap();
                                        return match v.as_ref() {
                                            Value::Boolean(b) => { Some(b.clone()) }
                                            Value::Nil => { None }
                                            Value::Number(n) => { Some(n.clone() != 0.0) }
                                            Value::String(s) => {
                                                Some(s.len() > 0)
                                            }
                                            Value::HashMap(hm) => {
                                                Some(!hm.is_empty())
                                            }
                                            Value::Array(a) => { Some(a.len() > 0) }
                                        }
                                    }
                                }
                                ConditionContents::Boolean(b) => { return Some(b); }
                                ConditionContents::Nil => { return None; }
                                ConditionContents::Number(n) => { return Some(n != 0.0) }
                                ConditionContents::String(s) => {
                                    return Some(s.len() > 0);
                                }
                                ConditionContents::HashMap(hm) => {
                                    return Some(!hm.is_empty());
                                }
                                ConditionContents::Array(a) => { return Some(a.len() > 0) }
                            }
                        }
                        Err(_) => {
                            panic!("Error parsing condition")
                        }
                    }
                } else {
                    comp_in_use.sort();
                    for comp in comp_in_use {
                        if !Self::is_in_quotes(content.clone(), comp.clone().name) {
                            let left: String = content.clone().chars().take(comp.location.unwrap()).collect();
                            let right: String = content.clone().chars().skip(comp.location.unwrap() + comp.clone().name.len()).take(content.len() - comp.location.unwrap() - comp.clone().name.len()).collect();

                            let processed_left = process_string_with_variables(left, Rc::clone(&vs), None, Some(true));
                            let processed_right = process_string_with_variables(right, Rc::clone(&vs), None, Some(true));

                            let processed_left_as_num = processed_left.parse::<f64>();
                            let processed_right_as_num = processed_right.parse::<f64>();

                            match comp.name.as_str() {
                                " gt " => {
                                    if processed_left_as_num.is_ok() && processed_right_as_num.is_ok() {
                                        return Some(processed_left_as_num.unwrap() > processed_right_as_num.unwrap());
                                    }
                                    return Some(processed_left > processed_right);
                                }
                                " gte " => {
                                    if processed_left_as_num.is_ok() && processed_right_as_num.is_ok() {
                                        return Some(processed_left_as_num.unwrap() >= processed_right_as_num.unwrap());
                                    }
                                    return Some(processed_left >= processed_right);
                                }
                                " lt " => {
                                    if processed_left_as_num.is_ok() && processed_right_as_num.is_ok() {
                                        return Some(processed_left_as_num.unwrap() < processed_right_as_num.unwrap());
                                    }
                                    return Some(processed_left < processed_right);
                                }
                                " lte " => {
                                    if processed_left_as_num.is_ok() && processed_right_as_num.is_ok() {
                                        return Some(processed_left_as_num.unwrap() <= processed_right_as_num.unwrap());
                                    }
                                    return Some(processed_left <= processed_right);
                                }
                                " eq " => {
                                    if processed_left_as_num.is_ok() && processed_right_as_num.is_ok() {
                                        return Some(processed_left_as_num.unwrap() == processed_right_as_num.unwrap());
                                    }
                                    return Some(processed_left == processed_right);
                                }
                                " neq " => {
                                    if processed_left_as_num.is_ok() && processed_right_as_num.is_ok() {
                                        return Some(processed_left_as_num.unwrap() != processed_right_as_num.unwrap());
                                    }
                                    return Some(processed_left != processed_right);
                                }
                                _ => {
                                    panic!("Something in comparisons went wrong")
                                }
                            }
                        }
                    }
                }
            }
        }
        None
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
}

pub(crate) fn process_condition(graphemes: Vec<&str>, variable_scope: Rc<RefCell<VariableScope>>) -> bool {
    let mut node = parse_condition_tree(graphemes);
    node.compute(variable_scope)
}

fn parse_condition_tree(graphemes: Vec<&str>) -> ConditionNode {
    let mut node = ConditionNode {
        contents: ConditionContents::Nil,
        junctions: Vec::new(),
        children: Vec::new(),
    };

    let mut inside_the_quotes = false;
    let mut used_quotes = "";
    let mut parenthesis_counter: usize = 0;
    let mut start: usize = 0;
    let mut end: usize = 0;
    let mut parethesis_start_idx = -1isize;
    while end < graphemes.len() {
        println!("{:?}", graphemes[end]);
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
                if parenthesis_counter == 1 && end <= isize::MAX as usize{
                    parethesis_start_idx = end as isize;
                }
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
                let mut local_end = end;
                while graphemes[start] == " " {
                    start += 1;
                }
                while graphemes[local_end - 1] == " " {
                     local_end -= 1;
                }

                if graphemes[start] == "(" && graphemes[local_end - 1] == ")" {
                    let try_parsing_inner = parse_condition_tree(graphemes[start + 1..local_end - 1].to_vec());
                    if let ConditionContents::String(contents) = try_parsing_inner.contents.clone() {
                        if contents.clone().len() == 0 {
                            node = try_parsing_inner.clone();
                        } else {
                            node.contents = ConditionContents::String(graphemes[start + 1..local_end - 1].join("").trim().to_string());
                        }
                    } else if try_parsing_inner.children.len() > 0 {
                        node = try_parsing_inner.clone();
                    }
                } else {
                    node.contents = ConditionContents::String(graphemes[start..local_end].join("").trim().to_string());
                }
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
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "true"),
            _ => panic!()
        }
    }

    #[test]
    fn parse_variable_to_node() {
        let cond = "my_var".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "my_var"),
            _ => panic!()
        }
    }

    #[test]
    fn parse_string_to_node() {
        let cond = "'str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "'str'"),
            _ => panic!()
        }
    }

    #[test]
    fn parse_string_to_node_with_backlash() {
        let cond = "'\\\\str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "'\\\\str'"),
            _ => panic!()
        }
    }

    #[test]
    fn parse_string_to_node_with_backlash_single_quote() {
        let cond = "'\'str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "'\'str'"),
            _ => panic!()
        }
    }

    #[test]
    fn parse_string_to_node_with_backlash_double_quote() {
        let cond = "'\\\"str'".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "'\\\"str'"),
            _ => panic!()
        }
    }

    #[test]
    fn parse_string_to_node_double() {
        let cond = "\"str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "\"str\""),
            _ => panic!()
        }
    }

    #[test]
    fn parse_string_to_node_double_with_backlash() {
        let cond = "\"\\\\str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "\"\\\\str\""),
            _ => panic!()
        }

    }

    #[test]
    fn parse_string_to_node_double_with_backlash_single_quote() {
        let cond = "\"\'str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "\"\'str\""),
            _ => panic!()
        }
    }

    #[test]
    fn parse_string_to_node_double_with_backlash_double_quote() {
        let cond = "\"\"str\"".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 0);
        match res.contents {
            ConditionContents::String(a) => assert_eq!(a, "\"\"str\""),
            _ => panic!()
        }
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

        assert_eq!(res.children.len(), 2);
        match res.children[0].clone().contents {
            ConditionContents::String(a) => assert_eq!(a, "my_var"),
            _ => panic!()
        }
        match res.children[1].clone().contents {
            ConditionContents::String(a) => assert_eq!(a, "not_my_var"),
            _ => panic!()
        }
        println!("{:?}", res);
        match res.clone().contents {
            ConditionContents::Nil => assert!(true),
            _ => panic!()
        }
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::And);
    }

    #[test]
    fn parse_or_to_node() {
        let cond = "my_var or not_my_var".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        println!("{:?}", res);
        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, ConditionContents::String("my_var".to_string()));
        assert_eq!(res.children[1].contents, ConditionContents::String("not_my_var".to_string()));
        assert_eq!(res.contents, ConditionContents::Nil);
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::Or);
    }

    #[test]
    fn parse_with_parenthesis_to_node() {
        let cond = "(my_var) and not_my_var".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, ConditionContents::String("my_var".to_string()));
        assert_eq!(res.children[1].contents, ConditionContents::String("not_my_var".to_string()));
        assert_eq!(res.contents, ConditionContents::Nil);
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::And);
    }

    #[test]
    fn parse_with_two_parenthesis_to_node() {
        let cond = "(my_var) and (not my_var)".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, ConditionContents::String("my_var".to_string()));
        assert_eq!(res.children[1].contents, ConditionContents::String("not my_var".to_string()));
        assert_eq!(res.contents, ConditionContents::Nil);
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::And);
    }

    #[test]
    fn parse_with_two_parenthesis_one_eq_to_node() {
        let cond = "(1 eq 1) and (not my_var)".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, ConditionContents::String("1 eq 1".to_string()));
        assert_eq!(res.children[1].contents, ConditionContents::String("not my_var".to_string()));
        assert_eq!(res.contents, ConditionContents::Nil);
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::And);
    }

    #[test]
    fn parse_with_one_parenthesis_one_eq_to_node() {
        let cond = "1 eq 1 and (not my_var)".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, ConditionContents::String("1 eq 1".to_string()));
        assert_eq!(res.children[1].contents, ConditionContents::String("not my_var".to_string()));
        assert_eq!(res.contents, ConditionContents::Nil);
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::And);
    }

    #[test]
    fn parse_with_one_or_in_parenthesis_to_node() {
        let cond = "(not my_var or my_var)".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        println!("{:?}", res);
        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, ConditionContents::String("not my_var".to_string()));
        assert_eq!(res.children[1].contents, ConditionContents::String("my_var".to_string()));
        assert_eq!(res.junctions[0], JunctionType::Or);
    }

    #[test]
    fn parse_with_one_parenthesis_one_or_in_parenthesis_to_node() {
        let cond = "1 eq 1 and (not my_var or my_var)".graphemes(true).collect::<Vec<&str>>();
        let res = parse_condition_tree(cond);

        println!("{:?}", res.children);
        assert_eq!(res.children.len(), 2);
        assert_eq!(res.children[0].contents, ConditionContents::String("1 eq 1".to_string()));
        assert_eq!(res.children[1].contents, ConditionContents::Nil);
        assert_eq!(res.children[1].children.len(), 2);
        assert_eq!(res.children[1].children[0].contents, ConditionContents::String("not my_var".to_string()));
        assert_eq!(res.children[1].children[1].contents, ConditionContents::String("my_var".to_string()));
        assert_eq!(res.children[1].junctions[0], JunctionType::Or);
        assert_eq!(res.contents, ConditionContents::Nil);
        assert_eq!(res.junctions.len(), 1);
        assert_eq!(res.junctions[0], JunctionType::And);
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
            contents: ConditionContents::Boolean(true),
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
            contents: ConditionContents::Boolean(false),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_var_boolean_true_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("test".to_string(), Rc::new(Value::String(String::from("test"))));
        }
        let node = ConditionNode {
            contents: ConditionContents::String("test".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        println!("{:?}", res);
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_gt_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("1 gt 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gt_equal_false_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 gt 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gt_numbers_true_res_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 gt 1".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_gte_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("1 gte 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gte_equals_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 gte 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_gte_greater_number_first_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("3 gte 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_lt_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("1 lt 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_lt_equal_false_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 lt 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_lt_numbers_true_res_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 lt 1".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_lte_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("1 lte 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_lte_equals_numbers_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 lte 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_lte_greater_number_first_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("3 lte 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_eq_greater_number_first_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("3 eq 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_eq_same_number_first_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 eq 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_neq_greater_number_first_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("3 neq 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_neq_same_number_first_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::String("2 neq 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gt_var_false_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("test".to_string(), Rc::new(Value::String(String::from("1".to_string()))));
        }
        let node = ConditionNode {
            contents: ConditionContents::String("test gt 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gt_var_false_equal_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("test".to_string(), Rc::new(Value::String(String::from("2".to_string()))));
        }
        let node = ConditionNode {
            contents: ConditionContents::String("test gt 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gt_var_true_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("test".to_string(), Rc::new(Value::String(String::from("3".to_string()))));
        }
        let node = ConditionNode {
            contents: ConditionContents::String("test gt 2".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_gt_var_two_vars_false_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("test".to_string(), Rc::new(Value::String("1".to_string())));
            x.borrow_mut().create_variable("other".to_string(), Rc::new(Value::String("2".to_string())));
        }
        let node = ConditionNode {
            contents: ConditionContents::String("test gt other".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gt_var_two_vars_equal_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("test".to_string(), Rc::new(Value::String(String::from("2".to_string()))));
            x.borrow_mut().create_variable("other".to_string(), Rc::new(Value::String(String::from("2".to_string()))));
        }
        let node = ConditionNode {
            contents: ConditionContents::String("test gt other".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_gt_var_two_vars_true_node() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("test".to_string(), Rc::new(Value::String("3".to_string())));
            x.borrow_mut().create_variable("other".to_string(), Rc::new(Value::String("2".to_string())));
        }
        let node = ConditionNode {
            contents: ConditionContents::String("test gt other".to_string()),
            junctions: vec![],
            children: vec![],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_eq_and_eq_both_true() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::Nil,
            junctions: vec![JunctionType::And],
            children: vec![
                ConditionNode {
                    contents: ConditionContents::String("1 eq 1".to_string()),
                    junctions: vec![],
                    children: vec![],
                },
                ConditionNode {
                    contents: ConditionContents::String("1 eq 1".to_string()),
                    junctions: vec![],
                    children: vec![],
                }
            ],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }

    #[test]
    fn resolve_eq_and_eq_one_true() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::Nil,
            junctions: vec![JunctionType::And],
            children: vec![
                ConditionNode {
                    contents: ConditionContents::String("2 eq 1".to_string()),
                    junctions: vec![],
                    children: vec![],
                },
                ConditionNode {
                    contents: ConditionContents::String("1 eq 1".to_string()),
                    junctions: vec![],
                    children: vec![],
                }
            ],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_eq_or_eq_both_false() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::Nil,
            junctions: vec![JunctionType::Or],
            children: vec![
                ConditionNode {
                    contents: ConditionContents::String("2 eq 1".to_string()),
                    junctions: vec![],
                    children: vec![],
                },
                ConditionNode {
                    contents: ConditionContents::String("2 eq 1".to_string()),
                    junctions: vec![],
                    children: vec![],
                }
            ],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, false);
    }

    #[test]
    fn resolve_eq_or_eq_one_true() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let node = ConditionNode {
            contents: ConditionContents::Nil,
            junctions: vec![JunctionType::Or],
            children: vec![
                ConditionNode {
                    contents: ConditionContents::String("1 eq 2".to_string()),
                    junctions: vec![],
                    children: vec![],
                },
                ConditionNode {
                    contents: ConditionContents::String("1 eq 1".to_string()),
                    junctions: vec![],
                    children: vec![],
                }
            ],
        };
        let res = node.compute(Rc::clone(&vs));
        assert_eq!(res, true);
    }
}
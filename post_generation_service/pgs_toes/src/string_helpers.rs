use std::cell::RefCell;
use std::ops::Deref;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;
use crate::variable_scope::VariableScope;

pub fn process_string_with_variables(s: String, vs: Rc<RefCell<VariableScope>>) -> String {
    let chars = s.graphemes(true).collect::<Vec<&str>>();

    let mut idx = 0;
    let mut result = String::new();
    while idx < chars.len() {
        match chars[idx] {
            "\"" => {
                let mut jdx = idx + 1;
                while jdx < chars.len() {
                    if chars[jdx] == "\"" && chars[jdx - 1] != "\\"{
                        result = format!("{}{}", result, chars[idx + 1..jdx].join(""));
                        idx = jdx + 1;
                        break;
                    } else {
                        jdx += 1;
                    }
                }
                if jdx == chars.len() {
                    let num_str = chars[idx..jdx].join("");
                    let num = num_str.parse::<i64>();
                    if num.is_ok() {
                        result = format!("{}{} ", result, num.unwrap());
                        idx = jdx + 1;
                        break;
                    } else {
                        panic!("Error parsing condition")
                    }
                }
            }
            "'" => {
                let mut jdx = idx + 1;
                while jdx < chars.len() {
                    if chars[jdx] == "'" && chars[jdx - 1] != "\\"{
                        result = format!("{}{}", result, chars[idx + 1..jdx].join(""));
                        idx = jdx + 1;
                        break;
                    } else {
                        jdx += 1;
                    }
                }
                if jdx == chars.len() {
                    let num_str = chars[idx..jdx].join("");
                    let num = num_str.parse::<i64>();
                    if num.is_ok() {
                        result = format!("{}{} ", result, num.unwrap());
                        idx = jdx + 1;
                        break;
                    } else {
                        panic!("Error parsing condition")
                    }
                }
            }
            _ => {
                let parsed_number = chars[idx].parse::<i64>();
                let next_parsed_number = chars[idx + 1].parse::<i64>();
                if (chars[idx] == "-" && next_parsed_number.is_ok()) || parsed_number.is_ok() {
                    let mut jdx = idx + 1;
                    while jdx < chars.len() {
                        if chars[jdx] == " " {
                            let num_str = chars[idx + 1..jdx].join("");
                            let num = num_str.parse::<i64>();
                            if num.is_ok() {
                                result = format!("{}{} ", result, num.unwrap());
                                idx = jdx + 1;
                                break;
                            } else {
                                panic!("Error parsing condition")
                            }
                        } else {
                            jdx += 1;
                        }
                    }
                    if jdx == chars.len() {
                        let num_str = chars[idx..jdx].join("");
                        let num = num_str.parse::<i64>();
                        if num.is_ok() {
                            result = format!("{}{} ", result, num.unwrap());
                            idx = jdx + 1;
                            break;
                        } else {
                            panic!("Error parsing condition")
                        }
                    }
                } else {
                    let mut jdx = idx + 1;
                    while jdx < chars.len() {
                        if chars[jdx] == " " {
                            let var_name = chars[idx + 1..jdx].join("");
                            let l = vs.try_borrow();
                            match l {
                                Ok(ref_vs) => {
                                    let k = ref_vs.deref().clone();
                                    let var_val = k.find_variable(String::from(var_name));
                                    if var_val.is_some() {
                                        result = format!("{}{} ", result, var_val.unwrap());
                                        idx = jdx + 1;
                                        break;
                                    }
                                }
                                Err(_) => {
                                    panic!("Error parsing condition")
                                }
                            }
                            idx = jdx + 1;
                        }
                    }
                }
            }
        }
    }
    result.trim().to_string()
}

#[cfg(test)]
mod node_tests {
    use super::*;

    #[test]
    fn parse_number() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("11");
        let result = process_string_with_variables(test_str.clone(), Rc::clone(&vs));
        assert_eq!(result, test_str);
    }

    #[test]
    fn parse_string() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("'string'");
        let result = process_string_with_variables(test_str.clone(), Rc::clone(&vs));
        assert_eq!(result, "string");
    }
}
use std::cell::RefCell;
use std::ops::Deref;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::value::Value;
use crate::variable_scope::VariableScope;

pub fn process_string_with_variables(s: Value, vs: Rc<RefCell<VariableScope>>, ignore_spaces: Option<bool>, is_condition: Option<bool>) -> String {
    let chars = s.to_string().graphemes(true).collect::<Vec<&str>>();

    let mut idx = 0;
    let mut result = String::new();
    while idx < chars.len() {
        let debug = chars[idx];
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
                    let num = num_str.parse::<f64>();
                    if num.is_ok() {
                        result = format!("{}{}", result, num.unwrap());
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
                    let num = num_str.parse::<f64>();
                    if num.is_ok() {
                        result = format!("{}{}", result, num.unwrap());
                        idx = jdx + 1;
                        break;
                    } else {
                        panic!("Error parsing condition")
                    }
                }
            }
            " " => {
                if ignore_spaces.is_some() && !ignore_spaces.unwrap() {
                    result = format!("{} ", result);
                }
                idx += 1;
            }
            _ => {
                let parsed_number = chars[idx].parse::<f64>();
                let mut next_parsed_number = None;
                if idx + 1 < chars.len() {
                    let temp_next_parsed_number = chars[idx + 1].parse::<f64>();
                    if temp_next_parsed_number.is_ok() {
                        next_parsed_number = Some(temp_next_parsed_number.unwrap());
                    }
                }
                if (chars[idx] == "-" && next_parsed_number.is_some()) || parsed_number.is_ok() {
                    let mut jdx = idx + 1;
                    while jdx < chars.len() {
                        if chars[jdx] == " " {
                            let num_str = chars[idx..jdx].join("");
                            let num = num_str.parse::<f64>();
                            if num.is_ok() {
                                result = format!("{}{}", result, num.unwrap());
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
                        let num = num_str.parse::<f64>();
                        if num.is_ok() {
                            result = format!("{}{}", result, num.unwrap());
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
                            let var_name = chars[idx..jdx].join("");
                            if var_name == "not" && is_condition.is_some() {
                                result = format!("{}{} ", result, var_name);
                                jdx += 1;
                                idx = jdx;
                                jdx += 1;
                            } else {
                                let l = vs.try_borrow();
                                match l {
                                    Ok(ref_vs) => {
                                        let k = ref_vs.deref().clone();
                                        let var_val = k.find_variable(String::from(var_name));
                                        if var_val.is_some() {
                                            result = format!("{}{}", result, var_val.unwrap());
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
                        } else {
                            jdx += 1;
                        }
                    }
                    if jdx == chars.len() {
                        let var_name = chars[idx..jdx].join("");
                        if var_name == "not" && is_condition.is_some() {
                                result = format!("{}{}", result, var_name);
                            } else {
                            let l = vs.try_borrow();
                            match l {
                                Ok(ref_vs) => {
                                    let k = ref_vs.deref().clone();
                                    let var_val = k.find_variable(String::from(var_name));
                                    if var_val.is_some() {
                                        result = format!("{}{}", result, var_val.unwrap());
                                        break;
                                    }
                                }
                                Err(_) => {
                                    panic!("Error parsing condition")
                                }
                            }
                        }
                        idx = jdx;
                    }
                }
            }
        }
    }
    result.trim().to_string()
}

#[cfg(test)]
mod node_tests {
    use pgs_common::value::Value;
    use super::*;

    #[test]
    fn parse_number() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("11");
        let result = process_string_with_variables(Value::from(test_str.clone()), Rc::clone(&vs), None, None);
        assert_eq!(result, test_str);
    }

    #[test]
    fn parse_string() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("'string'");
        let result = process_string_with_variables(Value::from(test_str.clone()), Rc::clone(&vs), None, None);
        assert_eq!(result, "string");
    }

    #[test]
    fn parse_string_number() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("'string' 23");
        let result = process_string_with_variables(Value::from(test_str.clone()), Rc::clone(&vs), None, None);
        assert_eq!(result, "string23");
    }

    #[test]
    fn parse_number_string() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("23 'string'");
        let result = process_string_with_variables(Value::from(test_str.clone()), Rc::clone(&vs), None, None);
        assert_eq!(result, "23string");
    }

    #[test]
    fn parse_var() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let var_str = String::from("test val");
        let var_name = String::from("test");
        let mut x = Rc::clone(&vs);
        x.borrow_mut().create_variable(var_name.clone(), Rc::new(Value::String(var_str.clone())));
        let result = process_string_with_variables(Value::String(var_name.clone()), Rc::clone(&vs), None, None);
        assert_eq!(result, var_str);
    }

    #[test]
    fn parse_not_string() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("not");
        let result = process_string_with_variables(Value::from(test_str.clone()), Rc::clone(&vs), None, Some(true));
        assert_eq!(result, "not");
    }

    #[test]
    fn parse_not_with_var_string() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("not test");
        let var_str = String::from("true");
        let var_name = String::from("test");

        let mut x = Rc::clone(&vs);
        x.borrow_mut().create_variable(var_name.clone(), Rc::new(Value::String(var_str.clone())));

        let result = process_string_with_variables(Value::from(test_str.clone()), Rc::clone(&vs), None, Some(true));
        assert_eq!(result, "not true");
    }

    #[test]
    fn parse_string_with_var_string() {
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let test_str = String::from("test 'st ' thing");
        let var_str = String::from("true");
        let var_name = String::from("test");

        let mut x = Rc::clone(&vs);
        x.borrow_mut().create_variable(var_name.clone(), Rc::new(Value::String(var_str.clone())));
        x.borrow_mut().create_variable("thing".to_string(), Rc::new(Value::String("is true".to_string())));

        let result = process_string_with_variables(Value::from(test_str.clone()), Rc::clone(&vs), None, Some(true));
        assert_eq!(result, "truest is true");
    }
}
use std::cell::RefCell;
use std::ops::Deref;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;
use crate::variable_scope::VariableScope;

pub fn process_string_with_variables(s: String, quote: &str, vs: Rc<RefCell<VariableScope>>) -> String {
    let chars = s.graphemes(true).collect::<Vec<&str>>();
    let result = String::new();

    let mut idx = 0;
    let mut temp_buffer = String::new();
    while idx < chars.len() {
        match chars[idx] {
            "\"" => {
                let mut jdx = idx + 1;
                while jdx < chars.len() {
                    if chars[jdx] == "\"" && chars[jdx - 1] != "\\"{
                        temp_buffer = format!("{}{}", temp_buffer, chars[idx + 1..jdx].join(""));
                        idx = jdx + 1;
                        break;
                    }
                }
            }
            "'" => {
                let mut jdx = idx + 1;
                while jdx < chars.len() {
                    if chars[jdx] == "'" && chars[jdx - 1] != "\\"{
                        temp_buffer = format!("{}{}", temp_buffer, chars[idx + 1..jdx].join(""));
                        idx = jdx + 1;
                        break;
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
                                temp_buffer = format!("{}{} ", temp_buffer, num.unwrap());
                                idx = jdx + 1;
                            } else {
                                panic!("Error parsing condition")
                            }
                            break;
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
                                    k.find_variable(String::from(var_name));
                                }
                                Err(_) => {
                                    panic!("Error parsing condition")
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    result
}
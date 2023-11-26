use std::cell::RefCell;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;
use crate::variable_scope::VariableScope;

pub fn process_string_with_variables(s: String, quote: &str, vs: Rc<RefCell<VariableScope>>) -> String {
    let chars = s.graphemes(true).collect::<Vec<&str>>();
    let mut temp = String::new();
    let result = String::new();

    let mut in_quotes = false;
    let mut quote = "";
    let mut idx = 0;
    let mut temp_buffer = String::new();
    while idx < chars.len() {
        match chars[idx] {
            "\"" => {
                let mut jdx = idx + 1;
                while jdx < chars.len() {
                    if chars[jdx] == "\"" && chars[jdx - 1] != "\\"{
                        temp_buffer.push_str(chars[idx + 1..jdx].iter().collect());
                        idx = jdx + 1;
                    }
                }
            }
            "'" => {
                let mut jdx = idx + 1;
                while jdx < chars.len() {
                    if chars[jdx] == "'" && chars[jdx - 1] != "\\"{
                        temp_buffer.push_str(chars[idx + 1..jdx].iter().collect());
                        idx = jdx + 1;
                    }
                }
            }
            _ => {
                temp_buffer.push_str(chars[idx]);
                idx += 1;
            }
        }
    }

    // let l = vs.try_borrow();
    // match l {
    //     Ok(ref_vs) => {
    //         let k = ref_vs.deref().clone();
    //         k.find_variable(part.clone());
    //     }
    //     Err(_) => {}
    // }



    result
}
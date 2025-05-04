use std::collections::HashMap;
use crate::node::Node;
use unicode_segmentation::UnicodeSegmentation;
use crate::data_type::DataType;
use crate::node_type::NodeType;

mod node;
mod data_type;
mod node_type;
mod conditions;
mod variable_scope;
mod toe_commands;

pub fn scan_toes(template: String) -> Node {
    let template_graphemes = template.graphemes(true).collect::<Vec<&str>>();
    let mut idx: usize = 0;
    let mut root_node = Node {
        name: "".to_string(),
        attributes: Default::default(),
        children: vec![],
        node_type: NodeType::ToeRoot,
        text_content: String::new(),
    };

    let mut current_node = &mut root_node;
    
    // let x = String::from("this is a test string");
    // let slice = &x[1..3];
    // println!("{}", slice); <!p>

    while template_graphemes.len() > idx {
        match template_graphemes[idx] {
            "<" => {
                if template_graphemes.len() >= idx + 8 && template_graphemes[idx..idx + 9].join("").starts_with("<![CDATA[") {
                    // handle CDATA
                } else if template_graphemes.len() >= idx + 3 && template_graphemes[idx..idx + 4].join("").starts_with("<!--") {
                    // handle comments
                } else {
                    match template_graphemes[idx + 1] { 
                        "!" => {
                            
                        },
                        "?" => {
                            
                        },
                        &_ => {
                            
                        }
                    }
                    // common code
                }
            }
            &_ => {
                // create text node
                let mut content = String::from(template_graphemes[idx]);
                let mut jdx = idx + 1;
                while template_graphemes.len() > jdx {
                    if template_graphemes[jdx] != "<" {
                        content.push(template_graphemes[jdx].parse().unwrap());
                        jdx += 1;
                    } else {
                        jdx -= 1;
                        break;
                    }
                }
                idx = jdx;
                current_node.children.push(Node {
                    name: "".to_string(),
                    attributes: Default::default(),
                    children: vec![],
                    node_type: NodeType::Text,
                    text_content: content,
                });
            }
        }
    }
    root_node
}

pub(crate) fn process_attributes(attr_string: String) -> HashMap<String, DataType> {
    let mut result = HashMap::new();
    let attr_arr = attr_string.graphemes(true).collect::<Vec<&str>>();
    let mut idx = 0;
    let mut is_key_mode = true;
    let mut current_value = String::new();
    let mut current_key = String::new();
    let mut value_single_quotes = false;
    while attr_arr.len() > idx {
        if is_key_mode {
            if attr_arr[idx] == "=" {
                is_key_mode = false;
                if attr_arr.len() > idx + 1 && attr_arr[idx + 1] == "'" {
                    value_single_quotes = true
                } else if attr_arr.len() > idx + 1 && attr_arr[idx + 1] == "\"" {
                    value_single_quotes = false
                } else if attr_arr.len() > idx + 1 {
                    panic!();
                }
                idx += 1;
            } else if attr_arr[idx] == " " && current_key.len() > 0 {
                result.insert(current_key.clone(), DataType::Nil);
                current_key = String::new();
                idx += 1;
            } else {
                current_key.push(attr_arr[idx].parse().unwrap());
                idx += 1;
            }
        } else {
            if value_single_quotes {
                if attr_arr[idx] == "'" && attr_arr[idx - 1] != "\\" {
                    if current_value.is_empty() {
                    } else {
                        result.insert(current_key.clone(), DataType::from(current_value.clone()));
                        current_key = String::new();
                        current_value = String::new();
                        is_key_mode = true;
                        idx += 1;
                    }
                } else {
                    current_value.push(attr_arr[idx].parse().unwrap());
                }
            } else {
                if attr_arr[idx] == "\"" && attr_arr[idx - 1] != "\\" {
                    if current_value.is_empty() {
                    } else {
                        result.insert(current_key.clone(), DataType::from(current_value.clone()));
                        current_key = String::new();
                        current_value = String::new();
                        is_key_mode = true;
                        idx += 1;
                    }
                } else {
                    current_value.push(attr_arr[idx].parse().unwrap());
                }
            }
            idx += 1;
        }
    }
    if current_key.len() > 0 {
        if current_value.len() == 0 {
            result.insert(current_key, DataType::Nil);
        }
    }
    result
}

#[cfg(test)]
mod node_parsing_tests {
    use crate::node_type::NodeType;
    use super::*;

    #[test]
    fn empty_works() {
        let empty = String::from("");
        let result = scan_toes(empty.clone());
        assert_eq!(result.children.len(), 0);
        assert_eq!(result.text_content.len(), 0);
    }

    #[test]
    fn single_text_works() {
        let text = String::from("text content for a node");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Text);
    }

    #[test]
    fn single_self_closing_tag_works() {
        let text = String::from("<img />");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn single_closed_tag_works() {
        let text = String::from("<a></a>");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn single_closed_tag_with_content_works() {
        let text = String::from("<a>content</a>");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn doctype_works() {
        let text = String::from("<!DOCTYPE html>");
        let result = scan_toes(text);
        println!("{:?}", result);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::DocumentTypeDefinition);
    }

    #[test]
    fn doctype_lower_case_works() {
        let text = String::from("<!doctype html>");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::DocumentTypeDefinition);
        println!("{:?}", result);
    }
    
    #[test]
    fn doctype_lower_case_works_temp() {
        let text = String::from("<!doctype html=\"4.0\">");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::DocumentTypeDefinition);
        println!("{:?}", result);
    }

    #[test]
    fn cdata_works() {
        let text = String::from("<![CDATA[cdata text content]]>");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::CDATA);
    }

    #[test]
    fn comment_works() {
        let text = String::from("<!-- comment text -->");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Comment);
        assert_eq!(result.children[0].text_content, " comment text ");
    }
    
    #[test]
    fn normal_node_with_attribute() {
        let text = String::from("<html lang=\"en\"></html>");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
        assert_eq!(result.children[0].attributes.len(), 1);
        assert_eq!(result.children[0].attributes.get("lang").unwrap().clone(), DataType::String("en".to_string()));
    }
    
    #[test]
    fn normal_node_with_attribute_single_quotes() {
        let text = String::from("<html lang='en'></html>");
        let result = scan_toes(text);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
        assert_eq!(result.children[0].attributes.len(), 1);
        assert_eq!(result.children[0].attributes.get("lang").unwrap().clone(), DataType::String("en".to_string()));
    }
}

#[cfg(test)]
mod attribute_parsing_tests {
    use super::*;

    #[test]
    fn empty_works() {
        let empty = String::from("");
        let result = process_attributes(empty.clone());
        assert_eq!(result.len(), 0);
    }

    #[test]
    fn attribute_only_works() {
        let attr = String::from("test");
        let result = process_attributes(attr.clone());
        assert_eq!(result.len(), 1);
    }

    #[test]
    fn two_attributes_works() {
        let attr = String::from("test another");
        let result = process_attributes(attr.clone());
        assert_eq!(result.len(), 2);
    }

    #[test]
    fn attribute_with_value_works() {
        let attr = String::from("test='abc'");
        let result = process_attributes(attr.clone());
        assert_eq!(result.len(), 1);
    }

    #[test]
    fn attribute_with_value_works_2() {
        let attr = String::from("test=\"abc\"");
        let result = process_attributes(attr.clone());
        assert_eq!(result.len(), 1);
    }

    #[test]
    fn two_attributes_combo_works() {
        let attr = String::from("test='abc' another");
        let result = process_attributes(attr.clone());
        assert_eq!(result.len(), 2);
        assert_eq!(result.get("test").unwrap().clone(), DataType::String("abc".parse().unwrap()));

    }

    #[test]
    fn two_attributes_combo_works_2() {
        let attr = String::from("another test='abc'");
        let result = process_attributes(attr.clone());
        assert_eq!(result.len(), 2);
        assert_eq!(result.get("test").unwrap().clone(), DataType::String("abc".parse().unwrap()));
    }

    #[test]
    fn three_attributes_combo_works() {
        let attr = String::from("another test='abc' yet");
        let result = process_attributes(attr.clone());
        assert_eq!(result.len(), 3);
        assert_eq!(result.get("test").unwrap().clone(), DataType::String("abc".parse().unwrap()));
    }
}


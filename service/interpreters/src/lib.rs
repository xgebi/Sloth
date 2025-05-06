use std::collections::HashMap;
use crate::node::Node;
use unicode_segmentation::UnicodeSegmentation;
use crate::data_type::DataType;
use crate::node_type::NodeType;
use crate::variable_scope::VariableScope;

mod node;
mod data_type;
mod node_type;
mod conditions;
mod variable_scope;
mod toe_commands;

pub fn scan_toes(template: String) -> Node {
    let template_graphemes = template.graphemes(true).collect::<Vec<&str>>();

    let mut root_node = Node {
        name: "".to_string(),
        attributes: Default::default(),
        children: vec![],
        node_type: NodeType::ToeRoot,
        text_content: String::new(),
    };

    inner_scan(template_graphemes, root_node)
}

pub fn compile_toes(root_node: Node, variable_scope: VariableScope, config: HashMap<String, DataType>) -> String {
    String::new()
}

fn inner_scan(template_graphemes: Vec<&str>, mut root_node: Node) -> Node { // figure out what to return, this function will be called recursively
    let mut idx: usize = 0;
    let mut current_node = Node::create("".to_string(), HashMap::new(), NodeType::Normal);
    let mut node_name = String::new();

    while template_graphemes.len() > idx {
        match template_graphemes[idx] {
            "<" => {
                if template_graphemes.len() >= idx + 8 && template_graphemes[idx..idx + 9].join("").starts_with("<![CDATA[") {
                    // create CDATA <![CDATA[cdata text content]]>
                    let mut jdx = idx + 9;
                    let mut content = String::new();
                    while template_graphemes.len() > jdx {
                        if template_graphemes[jdx] == "]" && template_graphemes[jdx + 1] == "]" && template_graphemes[jdx + 2] == ">" {
                            jdx += 3;
                            break;
                        } else {
                            content.push(template_graphemes[jdx].parse().unwrap());
                            jdx += 1;
                        }
                    }
                    idx = jdx;
                    root_node.children.push(Node {
                        name: String::new(),
                        attributes: Default::default(),
                        children: vec![],
                        node_type: NodeType::CDATA,
                        text_content: content,
                    });
                } else if template_graphemes.len() >= idx + 3 && template_graphemes[idx..idx + 4].join("").starts_with("<!--") {
                    // handle comments
                    let mut content = String::new();
                    let mut jdx = idx + 4;
                    while template_graphemes.len() > jdx {
                        if template_graphemes.len() > jdx + 2 && template_graphemes[jdx] == "-" &&
                            template_graphemes[jdx + 1] == "-" &&
                            template_graphemes[jdx + 2] == ">" {
                            break;
                        } else {
                            content.push(template_graphemes[jdx].parse().unwrap());
                            jdx += 1;
                        }
                    }
                    idx = jdx + 3;
                    root_node.children.push(Node {
                        name: "".to_string(),
                        attributes: Default::default(),
                        children: vec![],
                        node_type: NodeType::Comment,
                        text_content: content,
                    });
                } else {
                    match template_graphemes[idx + 1] {
                        "!" => {
                            current_node = Node::create_by_type(NodeType::DocumentTypeDefinition);
                            idx += 1;
                        },
                        "?" => {
                            current_node = Node::create_by_type(NodeType::DocumentTypeDefinition);
                            idx += 1;
                        },
                        &_ => {
                            current_node = Node::create_by_type(NodeType::Normal);
                        }
                    }
                    // common code
                    let mut jdx = idx + 1;
                    let mut no_attributes = false;
                    while jdx < template_graphemes.len() {
                        if template_graphemes[jdx] == " " || template_graphemes[jdx] == ">" {
                            current_node.name = node_name.clone();
                            node_name = String::new();
                            no_attributes = template_graphemes[jdx] == ">";
                            jdx += 1;
                            break;
                        } else {
                            node_name.push_str(template_graphemes[jdx]);
                        }
                        jdx += 1;
                    }
                    let mut key = String::new();
                    let mut value = String::new();
                    let mut is_key = true;
                    let mut quote = String::new();
                    while jdx < template_graphemes.len() && !no_attributes {
                        if (template_graphemes[jdx] == ">" || template_graphemes[jdx..jdx+2].join("") == "/>") && quote.trim().is_empty() {
                            let local_value = if value.is_empty() { DataType::Nil } else { DataType::from(format!("'{}'", value)) };
                            current_node.attributes.insert(key.clone(), local_value);
                            break;
                        }
                        if is_key {
                            if template_graphemes[jdx] == "=" || template_graphemes[jdx] == " " {
                                if template_graphemes[jdx] == "=" {
                                    is_key = false;
                                    if template_graphemes[jdx + 1] == "\"" || template_graphemes[jdx + 1] == "'" {
                                        quote = String::from(template_graphemes[jdx + 1]);
                                    } else {
                                        quote = String::from(" ");
                                    }
                                    jdx += 1
                                }
                                if template_graphemes[jdx] == " " {
                                    current_node.attributes.insert(key.clone(), DataType::Nil);
                                    key = String::new();
                                }
                            } else {
                                key.push_str(template_graphemes[jdx]);
                            }
                        } else {
                            if template_graphemes[jdx] == quote {
                                let data_type_value = DataType::from(format!("'{}'", value.clone()));
                                current_node.attributes.insert(key.clone(), data_type_value);
                                quote = String::new();
                                is_key = true;
                            } else {
                                value.push_str(template_graphemes[jdx]);
                            }
                        }
                        jdx += 1;
                    }
                    idx = jdx;
                    if current_node.node_type == NodeType::Normal && template_graphemes[jdx..jdx+2].join("") != "/>" {
                        let mut current_name_counter = 0;
                        let start_index = idx;
                        let mut end_index = idx - 1;
                        let mut next_index = idx;
                        let mut rest = template_graphemes[next_index..].join("");
                        let mut next_end = rest.find(format!("</{}>", current_node.name.clone()).as_str());
                        if next_end.is_some() {
                            end_index = start_index + next_end.unwrap();
                            next_end = Some(end_index);
                        }
                        
                        current_name_counter = rest.matches(format!("<{}", current_node.name.clone()).as_str()).count();
                        while next_end.is_some() && current_name_counter > 0 {
                            next_index = next_end.unwrap() + 1;
                            rest = template_graphemes[next_index..].join("");
                            next_end = rest.find(format!("</{}>", current_node.name.clone()).as_str());

                            if next_end.is_some() {
                                end_index = next_index + next_end.unwrap();
                            }

                            let from_start = template_graphemes[start_index..end_index + 1].join("");
                            current_name_counter = from_start.matches(format!("<{}", current_node.name.clone()).as_str()).count();
                            let current_close_name_counter = from_start.matches(format!("</{}>", current_node.name.clone()).as_str()).count();

                            if current_name_counter == current_close_name_counter {
                                break;
                            }
                        }
                        if start_index < end_index {
                            let child_string = &template_graphemes[start_index..end_index];
                            // process child string
                            let end_tag_string = format!("</{}>", current_node.clone().name).len();
                            let inner_scan_result = inner_scan(child_string.to_owned(), current_node);

                            // idx move to end of </tag>
                            jdx = end_index + end_tag_string;
                            root_node.children.push(inner_scan_result);
                        } else {
                            let end_tag_string = format!("</{}>", current_node.clone().name).len();
                            jdx += end_tag_string + 1;
                            root_node.children.push(current_node);
                        }
                    } else {
                        root_node.children.push(current_node);
                        if jdx + 2 <= template_graphemes.len() && template_graphemes[jdx..jdx+2].join("") == "/>" {
                            jdx += 2;
                        } else {
                            jdx += 1;
                        }
                    }
                    idx = jdx;
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
                root_node.children.push(Node {
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
        println!("{:?}", result);
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
        println!("{:?}", result);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn single_closed_tag_with_another_tag_and_content_work() {
        let text = String::from("<b><a>content</a></b>");
        let result = scan_toes(text);
        println!("{:?}", result);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn single_closed_tag_with_two_tags_and_content_work() {
        let text = String::from("<a><b>content A</b><u>content B</u></a>");
        let result = scan_toes(text);
        println!("{:?}", result);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn single_closed_tag_with_same_name_tag_and_content_work() {
        let text = String::from("<a><a>content</a></a>");
        let result = scan_toes(text);
        println!("{:?}", result);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn sibling_closed_tags_with_content_work() {
        let text = String::from("<a>content A</a><b>content B</b>");
        let result = scan_toes(text);
        println!("{:?}", result);
        assert_eq!(result.children.len(), 2);
        assert_eq!(result.children[0].node_type, NodeType::Normal);
    }

    #[test]
    fn doctype_works() {
        let text = String::from("<!DOCTYPE html>");
        let result = scan_toes(text);
        println!("{:?}", result);
        assert_eq!(result.children.len(), 1);
        assert_eq!(result.children[0].node_type, NodeType::DocumentTypeDefinition);
        println!("{:?}", result.children[0].attributes.get("html"));
        assert_eq!(result.children[0].attributes.get("html").is_some(), true);
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
        println!("{:?}", result);
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
    
    #[test]
    fn basic_page() {
        let template = String::from("<!doctype html><html><head><title>Basic page</title></head><body><h1>Basic page</h1><div><div>Some text in nested divs</div></div></body></html>");
        let result = scan_toes(template);
        
        assert_eq!(result.children.len(), 2);
        assert_eq!(result.children[0].name, "doctype");
        assert_eq!(result.children[1].name, "html");
        assert_eq!(result.children[1].children.len(), 2);
        assert_eq!(result.children[1].children[0].name, "head");
        assert_eq!(result.children[1].children[0].children.len(), 1);
        assert_eq!(result.children[1].children[0].children[0].name, "title");
        assert_eq!(result.children[1].children[0].children[0].children.len(), 1);
        assert_eq!(result.children[1].children[0].children[0].children[0].text_content, "Basic page");
        assert_eq!(result.children[1].children[1].name, "body");
        assert_eq!(result.children[1].children[1].children.len(), 2);
        assert_eq!(result.children[1].children[1].children[0].name, "h1");
        assert_eq!(result.children[1].children[1].children[0].children.len(), 1);
        assert_eq!(result.children[1].children[1].children[0].children[0].text_content, "Basic page");
        assert_eq!(result.children[1].children[1].children[1].name, "div");
        assert_eq!(result.children[1].children[1].children[1].children.len(), 1);
        assert_eq!(result.children[1].children[1].children[1].children[0].name, "div");
        assert_eq!(result.children[1].children[1].children[1].children[0].children.len(), 1);
        assert_eq!(result.children[1].children[1].children[1].children[0].children[0].text_content, "Some text in nested divs");
        
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


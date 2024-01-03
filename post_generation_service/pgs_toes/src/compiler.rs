use std::cell::{RefCell};
use std::collections::HashMap;
use std::fs;
use std::hash::Hash;
use std::ops::Deref;
use std::path::Path;
use std::rc::Rc;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use crate::conditions::process_condition;
use crate::parser::parse_toe;
use crate::string_helpers::process_string_with_variables;
use crate::variable_scope::VariableScope;

// TODO for future Sarah, look for ways to remove the unsafe blocks

pub(crate) fn compile_node_tree(root_node: Node, data: HashMap<String, String>) -> Node {
    let mut compiled_root_node = Node::create_node(None, Some(NodeType::Root));
    // Done redo the Rc to be mutable https://stackoverflow.com/questions/58599539/cannot-borrow-in-a-rc-as-mutable
    let var_scope = Rc::new(RefCell::new(VariableScope::create_from_hashmap(data)));
    for child in root_node.children {
        compiled_root_node.children.append(&mut compile_node(child, Rc::clone(&var_scope)));
    }

    compiled_root_node
}

fn compile_node(n: Node, vs: Rc<RefCell<VariableScope>>) -> Vec<Node> {
    let mut res = Vec::new();
    // 1. check if it's a toe's meta node
    if n.name.to_lowercase().starts_with("toe:") {
        return process_toe_elements(n.clone(), Rc::clone(&vs));
    }
    // 2. check attributes for toe's attributes
    if has_toe_attribute(n.clone().attributes) {
        res.extend(process_toe_attributes(n.clone(), Rc::clone(&vs)))
    }
    res
}

fn has_toe_attribute(hm: HashMap<String, Option<String>>) -> bool {
    let res = false;
    for key in hm.keys() {
        if key.to_lowercase().starts_with("toe:") {
            return true;
        }
    }
    res
}

fn process_toe_elements(n: Node, vs: Rc<RefCell<VariableScope>>) -> Vec<Node> {
    let mut res = Vec::new();
    match n.name.to_lowercase().as_str() {
        "toe:import" => {
            res.append(process_import_tag(n.clone(), Rc::clone(&vs)).as_mut());
        }
        "toe:fragment" => {
            let computed = process_fragment_tag(n.clone(), Rc::clone(&vs));
            res.extend(computed);
        }
        "toe:head" => {
            // TODO can wait until post generation is ready
        }
        "toe:footer" => {
            // TODO can wait until post generation is ready
        }
        _ => {
            // TODO
        }
    }

    res
}

fn process_import_tag(n: Node, vs: Rc<RefCell<VariableScope>>) -> Vec<Node> {
    let res = Vec::new();

    process_if_attribute(n.clone(), Rc::clone(&vs));

    let toe_file = String::from("toe_file");
    let l = vs.try_borrow();
    if l.is_ok() {
        let ref_vs = l.unwrap();
        let k = ref_vs.deref().clone();
        let folder_path = k.find_variable(String::from(toe_file));
        let cloned_n = n.clone();
        if cloned_n.attributes.contains_key("file") && folder_path.is_some() {
            let f = cloned_n.attributes.get("file").unwrap().to_owned().unwrap();
            let formatted_path = format!("{}/{}", folder_path.unwrap(), f);
            let fp = Path::new(&formatted_path);
            if fp.is_file() {
                let contents = fs::read_to_string(fp);
                if contents.is_ok() {
                    let result_temp = parse_toe(contents.unwrap());
                    if result_temp.is_ok() {
                        let mut res = Vec::new();
                        for child in result_temp.unwrap().clone().children {
                            res.extend(compile_node(child.clone(), Rc::clone(&vs)));
                        }
                        return res;
                    }
                }
            }
        }
    }
    res
}

fn process_fragment_tag(n: Node, vs: Rc<RefCell<VariableScope>>) -> Vec<Node> {
    let mut res = Vec::new();
    return if n.attributes.contains_key("toe:if") || n.attributes.contains_key("toe:for") {
        if n.attributes.contains_key("toe:for") {
            return process_for_attribute(n.clone(), Rc::clone(&vs));
        }

        let mut processed_node: Option<Node> = handle_if_switch(n.clone(), Rc::clone(&vs));

        if processed_node.is_some() {
            res.push(processed_node.unwrap());
        }

        res
    } else {
        n.children.clone()
    }
}

fn handle_if_switch(n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    if n.attributes.contains_key("toe:if") {
        let processed_node = process_if_attribute(n.clone(), Rc::clone(&vs));
        if processed_node.is_some() {
            return processed_node;
        }
    }
    Some(n)
}

fn process_toe_attributes(n: Node, vs: Rc<RefCell<VariableScope>>) -> Vec<Node> {
    // TODO write test cases
    let mut res = Vec::new();
    let mut processed_node: Option<Node> = handle_if_switch(n.clone(), Rc::clone(&vs));
    if processed_node.is_none() {
        return res;
    }

    if n.attributes.contains_key("toe:for") {
        return process_for_attribute(processed_node.unwrap().clone(), Rc::clone(&vs));
    }

    if n.attributes.contains_key("toe:text") {
        processed_node = process_text_attribute(processed_node.unwrap().clone(), Rc::clone(&vs));
    }

    if n.attributes.contains_key("toe:content") {
        processed_node = process_content_attribute(processed_node.unwrap().clone(), Rc::clone(&vs));
    }

    if n.name == "script" && n.attributes.contains_key("toe:inline-js") {
        processed_node = process_inline_js(n.clone(), Rc::clone(&vs));
    }

    // href, alt and src probably could be sorted with one function
    for (k, _) in n.attributes.clone() {
        if k.starts_with("toe:") && ["toe:for", "toe:text", "toe:content", "toe:inline-js"].contains(&k.as_str()) {
            processed_node = process_toe_attribute(n.clone(), k, Rc::clone(&vs));
        }
    }

    if processed_node.is_some() {
        res.push(processed_node.unwrap());
    }

    res
}

fn process_if_attribute(n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    if !n.attributes.contains_key("toe:if") {
        Some(n)
    } else {
        let m = n.attributes.get("toe:if").clone().unwrap().as_ref().unwrap();
        let res = process_condition(m.graphemes(true).collect::<Vec<&str>>(), Rc::clone(&vs));
        return if res { Some(n) } else { None }
    }
}

fn process_for_attribute(n: Node, vs: Rc<RefCell<VariableScope>>) -> Vec<Node> {
    let mut res: Vec<Node> = vec![];
    let cond = n.attributes.get("toe:for").unwrap().clone().unwrap();
    let parts = cond.split(" in ");
    let middle_vs = vs.try_borrow();
    if let Ok(inner_vs) = middle_vs {
        let arr_var = parts.last().unwrap();
        let var_exists = inner_vs.clone().variable_exists(&arr_var.to_string());
        if var_exists {
            // TODO implement for loop
        }
    }
    return res;
}

// toe:text escapes html characters
fn process_text_attribute(mut n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    // use https://docs.rs/html-escape/latest/html_escape/
    let content = n.attributes.get("toe:text").unwrap().clone().unwrap_or(String::new());
    let mut processed_string = process_string_with_variables(content.clone(), Rc::clone(&vs), Some(true), None);
    processed_string = html_escape::encode_safe(&processed_string).parse().unwrap();
    n.attributes.remove("toe:text");
    let text_node = Node::create_text_node(processed_string);
    n.children = vec![text_node];

    Some(n)
}

fn process_toe_attribute(mut n: Node, attribute_name: String, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    let content = n.attributes.get(attribute_name.as_str()).unwrap().clone().unwrap_or(String::new());
    let mut processed_string = process_string_with_variables(content.clone(), Rc::clone(&vs), Some(true), None);
    processed_string = html_escape::encode_safe(&processed_string).parse().unwrap();
    n.attributes.remove(attribute_name.as_str());
    let divider = attribute_name.clone().find(":").unwrap_or(0);
    let attr = &attribute_name[divider.clone() + 1..attribute_name.len()];
    n.attributes.insert(String::from(attr), Some(String::from(processed_string)));
    Some(n)
}

// toe:content does NOT escape html characters
fn process_content_attribute(mut n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    let content = n.attributes.get("toe:content").unwrap().clone().unwrap_or(String::new());
    let processed_string = process_string_with_variables(content.clone(), Rc::clone(&vs), Some(true), None);
    n.attributes.remove("toe:content");
    let text_node = Node::create_text_node(processed_string);
    n.children = vec![text_node];
    Some(n)
}

fn process_inline_js(mut n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    if n.children.len() == 1 && n.children[0].node_type == NodeType::Text {
        let mut i: usize = 0;
        let mut res = String::new();
        while i < n.children[0].content.len() {
            let o_start = n.children[0].content[i..].find("<(");
            let o_end = n.children[0].content[i..].find(")>");
            if o_start.is_some() && o_end.is_some() {
                let start = o_start.unwrap();
                let end = o_end.unwrap();
                let content = n.children[0].content[i + start + 2..i + end].to_string();
                let processed_content = process_string_with_variables(content.clone().trim().to_string(), Rc::clone(&vs), Some(true), None);
                res = format!("{}{}{}", res, n.children[0].content[i..start].to_string(), processed_content);
                i += end + 2;
            } else if o_start.is_some() && o_end.is_none() {
                panic!("Invalid script");
            } else {
                res = format!("{}{}", res, n.children[0].content[i..].to_string().clone());
                i = n.children[0].content.len();
            }
        }
        n.children[0].content = res;
    }
    Some(n)
}

#[cfg(test)]
mod compile_basic_tests {
    use std::collections::HashMap;
    use super::*;

    #[test]
    fn compile_root_node() {
        let root_node = Node {
            name: "".to_string(),
            node_type: NodeType::Root,
            attributes: HashMap::new(),
            children: vec![],
            content: "".to_string(),
        };
        let mut vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = compile_node(root_node, vs);
        assert_eq!(res.len(), 0);
    }
}

#[cfg(test)]
mod import_tests {
    use super::*;
    use std::env;

    #[test]
    fn path_is_not_defined_test() {
        let node = Node {
            name: "toe:import".to_string(),
            node_type: NodeType::Root,
            attributes: HashMap::new(),
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_import_tag(node, vs);
        assert_eq!(res.len(), 0);
    }

    #[test]
    fn path_is_defined_file_missing_test() {
        let node = Node {
            name: "toe:import".to_string(),
            node_type: NodeType::Root,
            attributes: HashMap::new(),
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let cd = env::current_dir().unwrap();
        let path = cd.join("test_data").to_str().unwrap().to_string();
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("toe_file".to_string(), path);
        }
        let res = process_import_tag(node, vs);
        assert_eq!(res.len(), 0);
    }

    #[test]
    fn empty_import_test() {
        let mut node = Node {
            name: "toe:import".to_string(),
            node_type: NodeType::Root,
            attributes: HashMap::new(),
            children: vec![],
            content: "".to_string(),
        };
        node.attributes.insert(String::from("file"), Some(String::from("empty.toe.html")));
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let cd = env::current_dir().unwrap();
        let path = cd.join("test_data").to_str().unwrap().to_string();
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("toe_file".to_string(), path);
        }
        let res = process_import_tag(node, vs);
        assert_eq!(res.len(), 0);
    }

    #[test]
    fn empty_fragment_import_test() {
        let mut node = Node {
            name: "toe:import".to_string(),
            node_type: NodeType::Root,
            attributes: HashMap::new(),
            children: vec![],
            content: "".to_string(),
        };
        node.attributes.insert(String::from("file"), Some(String::from("empty_fragment.toe.html")));
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let cd = env::current_dir().unwrap();
        let path = cd.join("test_data").to_str().unwrap().to_string();
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("toe_file".to_string(), path);
        }
        let res = process_import_tag(node, vs);
        assert_eq!(res.len(), 0);
    }

    #[test]
    fn fragment_with_div_import_test() {
        let mut node = Node {
            name: "toe:import".to_string(),
            node_type: NodeType::Root,
            attributes: HashMap::new(),
            children: vec![],
            content: "".to_string(),
        };
        node.attributes.insert(String::from("file"), Some(String::from("fragment_with_div.toe.html")));
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let cd = env::current_dir().unwrap();
        let path = cd.join("test_data").to_str().unwrap().to_string();
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("toe_file".to_string(), path);
        }
        let res = process_import_tag(node, vs);
        assert_eq!(res.len(), 1);
    }
}

#[cfg(test)]
mod check_toe_attributes_tests {
    use std::collections::HashMap;
    use super::*;

    #[test]
    fn has_toe_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        hm.insert(String::from("item1"), None);
        hm.insert(String::from("item2"), Some(String::from("val2")));
        hm.insert(String::from("toe:item3"), Some(String::from("val3")));
        let res = has_toe_attribute(hm);
        assert!(res);
    }

    #[test]
    fn has_no_toe_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        hm.insert(String::from("item1"), None);
        hm.insert(String::from("item2"), Some(String::from("val2")));
        hm.insert(String::from("item3"), Some(String::from("val3")));
        let res = has_toe_attribute(hm);
        assert!(!res);
    }

    #[test]
    fn empty_hashmap_test() {
        let hm: HashMap<String, Option<String>> = HashMap::new();
        let res = has_toe_attribute(hm);
        assert!(!res);
    }
}

#[cfg(test)]
mod check_toe_text_attribute_tests {
    use std::collections::HashMap;
    use super::*;

    #[test]
    fn has_text_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "'val3'";
        hm.insert(String::from("toe:text"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_text_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, "val3");
    }

    #[test]
    fn has_text_not_valid_html_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "'<val3'";
        hm.insert(String::from("toe:text"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_text_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, "&lt;val3");
    }

    #[test]
    fn has_text_with_variable_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "val3";
        let test_val = "other_val";
        hm.insert(String::from("toe:text"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable(test_text.to_string(), test_val.to_string());
        }
        let res = process_text_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, test_val);
    }

    #[test]
    fn has_text_with_variable_and_text_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "val3 ' is good'";
        let test_val = "other_val";
        hm.insert(String::from("toe:text"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("val3".to_string(), test_val.to_string());
        }
        let res = process_text_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, "other_val is good");
    }
}

#[cfg(test)]
mod check_toe_content_attribute_tests {
    use std::collections::HashMap;
    use super::*;

    #[test]
    fn has_content_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "'val3'";
        hm.insert(String::from("toe:content"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_content_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, "val3");
    }

    #[test]
    fn has_text_not_valid_html_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "'<val3'";
        hm.insert(String::from("toe:content"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_content_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, "<val3");
    }

    #[test]
    fn has_text_with_variable_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "val3";
        let test_val = "other_val";
        hm.insert(String::from("toe:content"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable(test_text.to_string(), test_val.to_string());
        }
        let res = process_content_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, test_val);
    }

    #[test]
    fn has_text_with_variable_and_text_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "val3 ' is good'";
        let test_val = "other_val";
        hm.insert(String::from("toe:content"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("val3".to_string(), test_val.to_string());
        }
        let res = process_content_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 0);
        assert_eq!(res.clone().unwrap().children.len(), 1);
        assert_eq!(res.clone().unwrap().children[0].content, "other_val is good");
    }
}

#[cfg(test)]
mod check_toe_misc_attribute_tests {
    use std::collections::HashMap;
    use super::*;

    #[test]
    fn has_alt_with_text_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "'All is good'";

        hm.insert(String::from("toe:alt"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_toe_attribute(n, String::from("toe:alt"), Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 1);
        assert!(res.clone().unwrap().attributes.contains_key("alt"));
        let mid_res = res.clone().unwrap().attributes.clone().get("alt").unwrap().clone().unwrap();
        assert_eq!(mid_res, "All is good");
    }

    #[test]
    fn has_alt_with_variable_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "val3";
        let test_val = "other_val";

        hm.insert(String::from("toe:alt"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("val3".to_string(), test_val.to_string());
        }
        let res = process_toe_attribute(n, String::from("toe:alt"), Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 1);
        assert!(res.clone().unwrap().attributes.contains_key("alt"));
        let mid_res = res.clone().unwrap().attributes.clone().get("alt").unwrap().clone().unwrap();
        assert_eq!(mid_res, "other_val");
    }

    #[test]
    fn has_alt_with_variable_and_text_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let test_text = "val3 ' is good ' val4";
        let test_val = "other_val";
        let test_val_2 = "as well";

        hm.insert(String::from("toe:alt"), Some(String::from(test_text)));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("val3".to_string(), test_val.to_string());
            x.borrow_mut().create_variable("val4".to_string(), test_val_2.to_string());
        }
        let res = process_toe_attribute(n, String::from("toe:alt"), Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.clone().unwrap().attributes.len(), 1);
        assert!(res.clone().unwrap().attributes.contains_key("alt"));
        let mid_res = res.clone().unwrap().attributes.clone().get("alt").unwrap().clone().unwrap();
        assert_eq!(mid_res, "other_val is good as well");
    }
}


#[cfg(test)]
mod check_toe_if_attribute_tests {
    use std::collections::HashMap;
    use super::*;

    #[test]
    fn has_no_if_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_if_attribute(n, Rc::clone(&vs));
        assert!(res.is_some());
    }

    #[test]
    fn has_false_if_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        hm.insert(String::from("toe:if"), Some(String::from("false")));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_if_attribute(n, Rc::clone(&vs));
        println!("{:?}", res);
        assert!(res.is_none());
    }

    #[test]
    fn has_true_if_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        hm.insert(String::from("toe:if"), Some(String::from("true")));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_if_attribute(n, Rc::clone(&vs));
        println!("{:?}", res);
        assert!(res.is_some());
    }

    #[test]
    fn has_conditional_if_attribute_test() {
        let mut hm: HashMap<String, Option<String>> = HashMap::new();
        hm.insert(String::from("toe:if"), Some(String::from("1 gt 0")));
        let n = Node {
            name: "p".to_string(),
            node_type: NodeType::Node,
            attributes: hm,
            children: vec![],
            content: "".to_string(),
        };
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_if_attribute(n, Rc::clone(&vs));
        println!("{:?}", res);
        assert!(res.is_some());
    }
}

#[cfg(test)]
mod toe_inline_js_tests {
    use std::collections::HashMap;
    use pgs_common::node::NodeType;
    use super::*;

    #[test]
    fn has_no_inline_js_test() {
        let mut script_node = Node::create_node(Some("script".to_string()), Some(NodeType::Node));
        let content_node = Node::create_text_node(String::from("const x = 1;"));
        script_node.children.push(content_node);
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_inline_js(script_node, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.unwrap().clone().children[0].content, "const x = 1;");
    }

    #[test]
    fn has_inline_js_as_variable_test() {
        let mut script_node = Node::create_node(Some("script".to_string()), Some(NodeType::Node));
        let content_node = Node::create_text_node(String::from("const x = <( val )>;"));
        script_node.children.push(content_node);
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("val".to_string(), "12".to_string());
        }
        let res = process_inline_js(script_node, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.unwrap().clone().children[0].content, "const x = 12;");
    }

    #[test]
    fn has_inline_js_as_variable_string_test() {
        let mut script_node = Node::create_node(Some("script".to_string()), Some(NodeType::Node));
        let content_node = Node::create_text_node(String::from("const x = <( val )>;"));
        script_node.children.push(content_node);
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        unsafe {
            let mut x = Rc::clone(&vs);
            x.borrow_mut().create_variable("val".to_string(), "'abc'".to_string());
        }
        let res = process_inline_js(script_node, Rc::clone(&vs));
        assert!(res.is_some());
        assert_eq!(res.unwrap().clone().children[0].content, "const x = 'abc';");
    }

    #[test]
    #[should_panic]
    fn has_incomplete_inline_js_test() {
        let mut script_node = Node::create_node(Some("script".to_string()), Some(NodeType::Node));
        let content_node = Node::create_text_node(String::from("const x = <( 1;"));
        script_node.children.push(content_node);
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_inline_js(script_node, Rc::clone(&vs));
    }
}

#[cfg(test)]
mod toe_for_tests {
    use std::collections::HashMap;
    use pgs_common::node::NodeType;
    use super::*;

    #[test]
    fn invalid_test() {
        let mut node = Node::create_node(Some("script".to_string()), Some(NodeType::Node));
        let mut attrs: HashMap<String, Option<String>> = HashMap::new();
        attrs.insert("toe:for".to_string(), Some("invalid".to_string()));
        node.attributes = attrs;
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_for_attribute(node, Rc::clone(&vs));
        assert_eq!(res.len(), 0);
    }

    #[test]
    fn simple_array_test() {
        let mut node = Node::create_node(Some("script".to_string()), Some(NodeType::Node));
        let mut attrs: HashMap<String, Option<String>> = HashMap::new();
        attrs.insert("toe:for".to_string(), Some("[1, 2, 3]".to_string()));
        attrs.insert("toe:text".to_string(), Some("itm".to_string()));
        node.attributes = attrs;
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_for_attribute(node, Rc::clone(&vs));
        assert_eq!(res.len(), 3);
        assert_eq!(res[0].content, "1");
        assert_eq!(res[1].content, "2");
        assert_eq!(res[2].content, "3");
    }

    #[test]
    fn array_of_objects_test() {
        let mut node = Node::create_node(Some("script".to_string()), Some(NodeType::Node));
        let mut attrs: HashMap<String, Option<String>> = HashMap::new();
        attrs.insert("toe:for".to_string(), Some("[{'item1': 'val1'},{'item2': 'val2'}]".to_string()));
        attrs.insert("toe:text".to_string(), Some("itm".to_string()));
        node.attributes = attrs;
        let vs = Rc::new(RefCell::new(VariableScope::create()));
        let res = process_for_attribute(node, Rc::clone(&vs));
        assert_eq!(res.len(), 2);
        assert_eq!(res[0].content, "val1");
        assert_eq!(res[1].content, "val2");

    }
}
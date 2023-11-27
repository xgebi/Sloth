use std::cell::{RefCell};
use std::collections::HashMap;
use std::fs;
use std::hash::Hash;
use std::ops::Deref;
use std::path::Path;
use std::rc::Rc;
use pgs_common::node::{Node, NodeType};
use crate::parser::parse_toe;
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
        return process_toe_elements(n, vs);
    }
    // 2. check attributes for toe's attributes
    if has_toe_attribute(n.attributes) {

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
    println!("{}", n.name);
    match n.name.to_lowercase().as_str() {
        "toe:import" => {
            res.append(process_import_tag(n.clone(), Rc::clone(&vs)).as_mut());
        }
        "toe:fragment" => {
            let computed = process_fragment_tag(n.clone(), Rc::clone(&vs));
            res.extend(computed);
        }
        "toe:head" => {

        }
        "toe:footer" => {

        }
        _ => {

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
            println!("{:?}", fp);
            if fp.is_file() {
                let contents = fs::read_to_string(fp);
                if contents.is_ok() {
                    let result_temp = parse_toe(contents.unwrap());
                    if result_temp.is_ok() {
                        println!("{:?}", result_temp.clone().unwrap());
                        let mut res = Vec::new();
                        for child in result_temp.unwrap().clone().children {
                            println!("{:?}", child.clone());
                            res.extend(compile_node(child.clone(), Rc::clone(&vs)));
                            println!("{:?}", res.clone());
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
        // I might have to rework this, ¿simplify?
        let mut processed_node: Option<Node> = handle_if_switch(n.clone(), Rc::clone(&vs));

        if n.attributes.contains_key("toe:for") && processed_node.is_some() {
            processed_node = process_for_attribute(processed_node.unwrap(), Rc::clone(&vs));
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
    let mut res = Vec::new();
    let mut processed_node: Option<Node> = handle_if_switch(n.clone(), Rc::clone(&vs));

    if n.attributes.contains_key("toe:for") {
        processed_node = process_for_attribute(n.clone(), Rc::clone(&vs));
    }

    if n.attributes.contains_key("toe:text") {

    }

    if n.attributes.contains_key("toe:content") {

    }

    if n.attributes.contains_key("toe:href") {

    }

    if n.attributes.contains_key("toe:alt") {

    }

    if n.attributes.contains_key("toe:src") {

    }

    if n.attributes.contains_key("toe:inline-js") {

    }

    if processed_node.is_some() {
        res.push(processed_node.unwrap());
    }

    res
}

fn process_if_attribute(n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    Some(n)
}

fn process_for_attribute(n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    Some(n)
}

// toe:text escapes html characters
fn process_text_attribute(mut n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    // use https://docs.rs/html-escape/latest/html_escape/
    let content = n.attributes.get("toe:text").unwrap().clone().unwrap_or(String::new());
    let mut processed_string = compile_text(content, Rc::clone(&vs));
    processed_string = html_escape::encode_safe(&processed_string).parse().unwrap();
    n.attributes.remove("toe:text");
    let text_node = Node::create_text_node(processed_string);
    n.children = vec![text_node];
    Some(n)
}

// toe:content does NOT escape html characters
fn process_content_attribute(mut n: Node, vs: Rc<RefCell<VariableScope>>) -> Option<Node> {
    let content = n.attributes.get("toe:content").unwrap().clone().unwrap_or(String::new());
    let processed_string = compile_text(content, Rc::clone(&vs));
    n.attributes.remove("toe:content");
    let text_node = Node::create_text_node(processed_string);
    n.children = vec![text_node];
    Some(n)
}

fn compile_text(s: String, vs: Rc<RefCell<VariableScope>>) -> String {
    s
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
use std::collections::HashMap;
use std::hash::Hash;
use std::path::Path;
use pgs_common::node::{Node, NodeType};
use crate::variable_scope::VariableScope;

pub(crate) fn compile_node_tree(root_node: Node, data: HashMap<String, String>) -> Node {
    let mut compiled_root_node = Node::create_node(None, Some(NodeType::Root));
    let mut var_scope = VariableScope::create_from_hashmap(data);
    for child in root_node.children {
        compiled_root_node.children.append(&mut compile_node(child, &mut var_scope))
    }

    compiled_root_node
}

fn compile_node(n: Node, vs: &mut VariableScope) -> Vec<Node> {
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

fn process_toe_elements(n: Node, vs: &mut VariableScope) -> Vec<Node> {
    let mut res = Vec::new();

    match n.name.to_lowercase().as_str() {
        "toe:import" => {

        }
        "toe:fragment" => {

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

fn process_import_tag(n: Node, vs: &mut VariableScope) -> Vec<Node> {
    let res = Vec::new();

    process_if_attribute(n.clone(), vs);

    let toe_file = String::from("toe_file");

    let folder_path = vs.clone().find_variable(&toe_file);
    let cloned_n = n.clone();
    if cloned_n.attributes.contains_key("file") && folder_path.is_some() {
        let f = cloned_n.attributes.get("file").unwrap().to_owned().unwrap();
        let formatted_path = format!("{}/{}", folder_path.unwrap(), f);
        let fp = Path::new(&formatted_path);
        if fp.is_file() {

        }

    }

    res
}

fn process_toe_attributes(n: Node, vs: &mut VariableScope) -> Vec<Node> {
    let mut res = Vec::new();

    match n.name.to_lowercase().as_str() {
        "toe:if" => {
            let processed_node = process_if_attribute(n, vs);
            if processed_node.is_some() {
                res.push(processed_node.unwrap());
            }
        }
        "toe:for" => {

        }
        "toe:text" => {

        }
        "toe:content" => {

        }
        "toe:href" => {

        }
        "toe:alt" => {

        }
        "toe:src" => {

        }
        "toe:inline-js" => {

        }
        _ => {

        }
    }

    res
}

fn process_if_attribute(n: Node, vs: &mut VariableScope) -> Option<Node> {
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
        let mut vs = VariableScope::create();
        let res = compile_node(root_node, &mut vs);
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
        let mut vs = VariableScope::create();
        let res = process_import_tag(node, &mut vs);
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
        let mut vs = VariableScope::create();
        let cd = env::current_dir().unwrap();
        let mut path = cd.join("test_data").to_str().unwrap().to_string();
        vs.assign_variable(&"toe_file".to_string(), &mut path);
        let res = process_import_tag(node, &mut vs);
        assert_eq!(res.len(), 0);
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
use std::collections::HashMap;
use std::fs;
use std::hash::Hash;
use std::path::Path;
use std::rc::Rc;
use pgs_common::node::{Node, NodeType};
use crate::parser::parse_toe;
use crate::variable_scope::VariableScope;

pub(crate) fn compile_node_tree(root_node: Node, data: HashMap<String, String>) -> Node {
    let mut compiled_root_node = Node::create_node(None, Some(NodeType::Root));
    // TODO redo the Rc to be mutable https://stackoverflow.com/questions/58599539/cannot-borrow-in-a-rc-as-mutable
    let var_scope = Rc::new(VariableScope::create_from_hashmap(data));
    for child in root_node.children {
        compiled_root_node.children.append(&mut compile_node(child, Rc::clone(&var_scope)));
    }

    compiled_root_node
}

fn compile_node(n: Node, vs: Rc<VariableScope>) -> Vec<Node> {
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

fn process_toe_elements(n: Node, vs: Rc<VariableScope>) -> Vec<Node> {
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

fn process_import_tag(n: Node, vs: Rc<VariableScope>) -> Vec<Node> {
    let res = Vec::new();

    process_if_attribute(n.clone(), Rc::clone(&vs));

    let toe_file = String::from("toe_file");

    let folder_path = Rc::try_unwrap(vs).unwrap().find_variable(toe_file); //.find_variable(&toe_file);
    let cloned_n = n.clone();
    if cloned_n.attributes.contains_key("file") && folder_path.is_some() {
        let f = cloned_n.attributes.get("file").unwrap().to_owned().unwrap();
        let formatted_path = format!("{}/{}", folder_path.unwrap(), f);
        let fp = Path::new(&formatted_path);
        if fp.is_file() {
            let contents = fs::read_to_string(fp);
            if contents.is_ok() {
                let result = parse_toe(contents.unwrap());
                // TODO add compilation step here
                if result.is_ok() {
                    return result.unwrap().children;
                }
            }
        }
    }
    res
}

fn process_toe_attributes(n: Node, vs: Rc<VariableScope>) -> Vec<Node> {
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

fn process_if_attribute(n: Node, vs: Rc<VariableScope>) -> Option<Node> {
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
        let mut vs = Rc::new(VariableScope::create());
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
        let mut vs = Rc::new(VariableScope::create());
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
        let mut vs = Rc::new(VariableScope::create());
        let cd = env::current_dir().unwrap();
        let mut path = cd.join("test_data").to_str().unwrap().to_string();
        vs.create_variable("toe_file".to_string(), path);
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
        let mut vs = Rc::new(VariableScope::create());
        let cd = env::current_dir().unwrap();
        let mut path = cd.join("test_data").to_str().unwrap().to_string();
        vs.create_variable("toe_file".to_string(), path);
        let res = process_import_tag(node, vs);
        assert_eq!(res.len(), 0);
    }

    #[test]
    fn single_template_import_test() {
        let mut node = Node {
            name: "toe:import".to_string(),
            node_type: NodeType::Root,
            attributes: HashMap::new(),
            children: vec![],
            content: "".to_string(),
        };
        node.attributes.insert(String::from("file"), Some(String::from("single_template.toe.html")));
        let mut vs = Rc::new(VariableScope::create());
        let cd = env::current_dir().unwrap();
        let mut path = cd.join("test_data").to_str().unwrap().to_string();
        vs.create_variable("toe_file".to_string(), path);
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
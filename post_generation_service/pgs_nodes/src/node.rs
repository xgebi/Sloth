use std::collections::HashMap;
use std::borrow::Borrow;

#[derive(PartialEq, Eq, Debug)]
pub enum NodeType {
    Node,
    Processing,
    Text,
    Comment
}

pub struct Node {
    pub name: String,
    pub node_type: NodeType,
    pub attributes: HashMap<String, String>,
    pub children: Option<Vec<Node>>,
}
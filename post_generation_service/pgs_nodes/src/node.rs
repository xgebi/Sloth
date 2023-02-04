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
    pub content: Option<String>,
}

impl Node {
    fn is_unpaired(tag_name: String) -> bool {
        let unpaired_tags = ["base", "br", "meta", "hr", "img", "track", "source", "embed", "col", "input", "link"];
        unpaired_tags.contains(&&*tag_name)
    }

    fn is_always_paired(tag_name: String) -> bool {
        let paired_tags = ["script"];
        paired_tags.contains(&&*tag_name)
    }

    pub fn create_node(name: Option<String>) -> Node {
        Node{
            name: name.unwrap(),
            node_type: NodeTypes::Node,
            attributes: HashMap::new(),
            content: None,
            children: Some(Vec::new()),
        }
    }
}
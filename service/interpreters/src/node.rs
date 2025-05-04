use std::collections::HashMap;
use std::fmt::Display;
use crate::data_type::DataType;
use crate::node_type::NodeType;

#[derive(Debug, Clone)]
pub struct Node {
    pub name: String,
    pub attributes: HashMap<String, DataType>,
    pub children: Vec<Node>,
    pub node_type: NodeType,
    pub text_content: String,
}

impl Node {
    pub fn create_by_type(node_type: NodeType) -> Self {
        Node {
            name: "".to_string(),
            attributes: Default::default(),
            children: vec![],
            node_type,
            text_content: "".to_string(),
        }
    }
    
    pub fn create(name: String, attributes: HashMap<String, DataType>, node_type: NodeType) -> Self {
        Node {
            name,
            attributes,
            children: Vec::new(),
            node_type,
            text_content: String::new(),
        }
    }
}

impl Display for Node {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut result = String::from("<");
        match self.node_type {
            _ => {
                result.push(self.name.parse().unwrap());
            }
        }
        for attribute in self.attributes.clone() {
            result.push_str(format!("{}=\"{}\"", attribute.0, attribute.1).as_str());
        }
        write!(f, "{}", result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let tag = "b".to_string();
        let n = Node::create(tag.clone(), HashMap::new(), NodeType::Normal);
        assert_eq!(n.name, tag);
        assert_eq!(n.attributes.len(), 0);
        assert_eq!(n.children.len(), 0);
    }
}
use std::collections::HashMap;
use std::fmt::{format, Display};
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
    
    pub fn create_normal_node(name: String) -> Self {
        Node {
            name,
            attributes: Default::default(),
            children: vec![],
            node_type: NodeType::Normal,
            text_content: "".to_string(),
        }
    }
    
    pub fn create_text_node(text_content: String) -> Self {
        Node {
            name: "".to_string(),
            attributes: Default::default(),
            children: vec![],
            node_type: NodeType::Normal,
            text_content,
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
    
    pub fn is_unpaired(tag_name: String) -> bool {
        let unpaired_tags = ["base", "br", "meta", "hr", "img", "track", "source", "embed", "col", "input", "link"];
        unpaired_tags.contains(&&*tag_name)
    }

    fn is_always_paired(tag_name: String) -> bool {
        let paired_tags = ["script"];
        paired_tags.contains(&&*tag_name)
    }
}

impl Display for Node {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let no_angle_brackets = [NodeType::ToeRoot, NodeType::Text].contains(&self.node_type.clone());
        let mut result = if no_angle_brackets { String::new() } else { String::from("<") };
        match self.node_type {
            NodeType::DocumentTypeDefinition => {
                result.push_str("!");
            }
            NodeType::Processing => {
                result.push_str("?");
            }
            _ => {
                
            }
        }
        result.push_str(self.name.as_str());
        if !self.attributes.is_empty() {
            result.push_str(" ");
        }
        for attribute in self.attributes.clone() {
            result.push_str(format!("{}=\"{}\"", attribute.0, attribute.1).as_str());
            result.push_str(" ");
        }
        result = result.trim().to_string();
        if !Node::is_unpaired(self.name.clone()) ||
            Node::is_always_paired(self.name.clone()) {
            if self.node_type == NodeType::Processing {
                result.push_str("?");
            }
            if !no_angle_brackets {
                result.push_str(">");
            }
            if self.children.clone().is_empty() {
                result.push_str(self.text_content.as_str());
            } else {
                for child in self.children.clone() {
                    result.push_str(child.to_string().as_str());
                }
            }
            if !no_angle_brackets {
                result.push_str(format!("</{}>", self.name).as_str());
            }
        } else {
            if !no_angle_brackets { result.push_str("/>"); };
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
    
    #[test]
    fn is_tag_paired() {
        assert_eq!(Node::is_always_paired(String::from("script")), true);
    }

    #[test]
    fn is_not_tag_paired() {
        assert_eq!(Node::is_always_paired(String::from("br")), false);
    }

    #[test]
    fn is_tag_unpaired() {
        assert_eq!(Node::is_unpaired(String::from("br")), true);
    }

    #[test]
    fn is_not_tag_unpaired() {
        assert_eq!(Node::is_unpaired(String::from("div")), false);
    }
    
    #[test]
    fn display_node() {
        let mut attributes = HashMap::new();
        attributes.insert(String::from("key"), DataType::from("'value'".to_string()));
        
        let n = Node {
            name: "my-tag".to_string(),
            attributes,
            children: vec![],
            node_type: NodeType::Normal,
            text_content: "Node's text content".to_string(),
        };
        
        let result = n.to_string();
        assert_eq!(result, "<my-tag key=\"value\">Node's text content</my-tag>");
    }
    
    #[test]
    fn display_node_with_child_node() {
        let mut attributes = HashMap::new();
        attributes.insert(String::from("key"), DataType::from("'value'".to_string()));
        
        let child = Node {
            name: "my-tag".to_string(),
            attributes: Default::default(),
            children: vec![],
            node_type: NodeType::Normal,
            text_content: "Node's text content".to_string(),
        };
        
        let n = Node {
            name: "my-tag".to_string(),
            attributes,
            children: vec![child],
            node_type: NodeType::Normal,
            text_content: "Node's text content".to_string(),
        };
        
        let result = n.to_string();
        assert_eq!(result, "<my-tag key=\"value\"><my-tag>Node's text content</my-tag></my-tag>");
    }
}
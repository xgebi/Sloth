use std::collections::HashMap;
use std::borrow::Borrow;

#[derive(PartialEq, Eq, Debug, Copy, Clone)]
pub enum NodeType {
    Node,
    Processing,
    Text,
    Comment,
    Root
}

#[derive(Clone, Debug)]
pub struct Node {
    pub name: String,
    pub node_type: NodeType,
    pub attributes: HashMap<String, String>,
    pub children: Vec<Node>,
    pub content: String,
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

    pub fn create_node(name: Option<String>, node_type: Option<NodeType>) -> Node {
        Node {
            name: name.unwrap_or_default(),
            node_type: node_type.unwrap_or_else(|| NodeType::Node),
            attributes: HashMap::new(),
            content: String::new(),
            children: Vec::new(),
        }
    }

    pub fn create_processing_node() -> Node {
        Node{
            name: String::new(),
            node_type: NodeType::Processing,
            attributes: HashMap::new(),
            content: String::new(),
            children: Vec::new(),
        }
    }

    pub fn create_text_node(content: String) -> Node {
        Node {
            name: String::new(),
            node_type: NodeType::Text,
            attributes: HashMap::new(),
            content,
            children: Vec::new()
        }
    }

    pub fn create_comment_node(content: String) -> Node {
        Node {
            name: String::new(),
            node_type: NodeType::Comment,
            attributes: HashMap::new(),
            content,
            children: Vec::new()
        }
    }

    pub fn add_child(&mut self, n: Node) {
        self.children.push(n);
    }

    pub fn to_string(&self) -> String {
        match self.node_type {
            NodeType::Node =>  { self.node_to_string() }
            NodeType::Processing => { self.processing_node_to_string() }
            NodeType::Text => { self.text_node_to_string() }
            NodeType::Comment => {self.comment_node_to_string() }
            NodeType::Root => {self.root_node_to_string()}
        }
    }

    fn root_node_to_string(&self) -> String {
        let mut result = String::new();

        for child in &self.children {
            result += child.to_string().as_str();
        }

        result
    }

    fn node_to_string(&self) -> String {
        let mut result = String::new();
        result += &*format!("<{} ", self.name.clone());
        for (key, value) in self.attributes.iter() {
            result += &*format!("{}=\"{}\"", key, value);
        }

        if !Node::is_unpaired(self.name.clone()) ||
            Node::is_always_paired(self.name.clone()) {
            result = result.trim().parse().unwrap();
            result += &*format!(">");

            for child in &self.children {
                result += child.to_string().as_str();
            }

            result += &*format!("</{}>", self.name.clone());
        } else {
            result += &*format!("/>");
        }

        result
    }

    fn processing_node_to_string(&self) -> String {
        let mut result = String::new();
        result += &*format!("<?{} ", self.name.clone());
        for (key, value) in self.attributes.iter() {
            result += &*format!("{}=\"{}\"", key, value);
        }
        result += &*format!(" ?>");
        result
    }

    fn text_node_to_string(&self) -> String {
        if self.content.len() > 0 {
            return self.content.clone();
        }
        String::new()
    }

    fn comment_node_to_string(&self) -> String {
        if self.content.len() > 0 {
            return String::from(format!("<!-- {} -->", self.content.clone()));
        }
        String::new()
    }
}

#[cfg(test)]
mod tests {
    use crate::node::{Node, NodeType};

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

    // Node tests
    #[test]
    fn test_creating_node() {
        let root_node = Node::create_node(None, None);
        assert_eq!(root_node.node_type, NodeType::Node);
    }

    #[test]
    fn unpaired_node_to_string() {
        let mut node = Node::create_node(Some(String::from("br")), None);
        assert_eq!(node.to_string(), "<br />");
    }

    #[test]
    fn paired_childless_node_to_string() {
        let node = Node::create_node(Some(String::from("br")), None);
        assert_eq!(node.to_string(), "<br />");
    }

    #[test]
    fn paired_node_to_string() {
        let mut node = Node::create_node(Some(String::from("div")), None);

        node.children.push(Node::create_node(Some(String::from("br")), None));

        assert_eq!(node.to_string(), "<div><br /></div>");
    }

    // Processing nodes
    #[test]
    fn test_creating_processing_node() {
        let processing_node = Node::create_processing_node();
        assert_eq!(processing_node.node_type, NodeType::Processing);
    }

    #[test]
    fn processing_node_to_string() {
        let mut processing_node = Node::create_processing_node();
        processing_node.name = String::from("processing");
        processing_node.attributes.insert(String::from("attr"), String::from("attr-val"));
        assert_eq!(processing_node.to_string(), "<?processing attr=\"attr-val\" ?>");
    }

    // Text nodes
    #[test]
    fn test_creating_text_node() {
        let text_node = Node::create_text_node("text".to_string());
        assert_eq!(text_node.node_type, NodeType::Text);
    }

    #[test]
    fn text_node_to_string() {
        let text_node = Node::create_text_node("text".to_string());
        assert_eq!(text_node.to_string(), "text");
    }

    // Processing nodes
    #[test]
    fn test_creating_comment_node() {
        let comment_node = Node::create_comment_node("this is comment".to_string());
        assert_eq!(comment_node.node_type, NodeType::Comment);
    }

    #[test]
    fn comment_node_to_string() {
        let comment_node = Node::create_comment_node("this is comment".to_string());
        assert_eq!(comment_node.to_string(), "<!-- this is comment -->");
    }

    #[test]
    fn root_node_to_string() {
        let mut root_node = Node::create_node(None, Some(NodeType::Root));
        let child = Node::create_node(Some(String::from("p")), None);
        root_node.add_child(child);
        assert_eq!(root_node.to_string(), "<p></p>")
    }
}
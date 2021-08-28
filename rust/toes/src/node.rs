use std::collections::HashMap;
use std::borrow::Borrow;

#[derive(PartialEq, Eq, Debug)]
pub(crate) enum NodeTypes {
    Node,
    Root,
    Processing,
    Directive,
    Text,
    Comment,
}

pub struct ToeTreeTop {
    pub children: Vec<ToeNode>,
}

pub struct ToeNode {
    pub(crate) name: Option<String>,
    pub(crate) node_type: NodeTypes,
    pub(crate) attributes: HashMap<String, String>,
    pub(crate) content: Option<String>,
    pub(crate) children: Option<Vec<ToeNode>>,
}

impl ToeNode {
    fn is_unpaired(tag_name: String) -> bool {
        let unpaired_tags = ["base", "br", "meta", "hr", "img", "track", "source", "embed", "col", "input", "link"];
        unpaired_tags.contains(&&*tag_name)
    }

    fn is_always_paired(tag_name: String) -> bool {
        let paired_tags = ["script"];
        paired_tags.contains(&&*tag_name)
    }

    pub fn create_node(name: Option<String>) -> ToeNode {
        ToeNode{
            name,
            node_type: NodeTypes::Node,
            attributes: HashMap::new(),
            content: None,
            children: Some(Vec::new()),
        }
    }

    pub fn create_root_node() -> ToeNode {
        ToeNode{
            name: Some(String::from("xml")),
            node_type: NodeTypes::Root,
            attributes: HashMap::new(),
            content: None,
            children: None
        }
    }

    pub fn create_processing_node() -> ToeNode {
        ToeNode{
            name: Some(String::from("xml")),
            node_type: NodeTypes::Root,
            attributes: HashMap::new(),
            content: None,
            children: None,
        }
    }

    pub fn to_string(&self) -> String {
        match self.node_type {
            NodeTypes::Node =>  { self.node_to_string() }
            NodeTypes::Root => { self.root_node_to_string() }
            NodeTypes::Processing => { self.processing_node_to_string() }
            NodeTypes::Directive => { self.directive_node_to_string() }
            NodeTypes::Text => { self.text_node_to_string() }
            NodeTypes::Comment => {self.comment_node_to_string() }
        }
    }

    fn node_to_string(&self) -> String {
        let mut result = String::new();
        result += &*format!("<{} ", self.name.as_ref().unwrap());
        for (key, value) in self.attributes.iter() {
            result += &*format!("{}=\"{}\"", key, value);
        }
        if let Some(name) = self.name.as_ref() {
            if !ToeNode::is_unpaired(name.clone()) ||
                ToeNode::is_always_paired(name.clone()) {
                result = result.trim().parse().unwrap();
                result += &*format!(">");
                if let Some(children) = &self.children {
                    for child in children {
                        result += child.to_string().as_str();
                    }
                }
                result += &*format!("</{}>", self.name.as_ref().unwrap());
            } else {
                result += &*format!("/>");
            }
        }
        result
    }

    fn root_node_to_string(&self) -> String {
        let mut result = String::new();
        result += &*format!("<?{} ", self.name.as_ref().unwrap());
        for (key, value) in self.attributes.iter() {
            result += &*format!("{}=\"{}\"", key, value);
        }
        result += &*format!(" ?>");
        result
    }

    fn processing_node_to_string(&self) -> String {
        String::new()
    }

    fn directive_node_to_string(&self) -> String {
        String::new()
    }

    fn text_node_to_string(&self) -> String {
        String::new()
    }

    fn comment_node_to_string(&self) -> String {
        String::new()
    }
}

#[cfg(test)]
mod tests {
    use crate::ToeNode;
    use crate::node::NodeTypes;
    use unicode_segmentation::UnicodeSegmentation;

    #[test]
    fn is_tag_paired() {
        assert_eq!(ToeNode::is_always_paired(String::from("script")), true);
    }

    #[test]
    fn is_not_tag_paired() {
        assert_eq!(ToeNode::is_always_paired(String::from("br")), false);
    }

    #[test]
    fn is_tag_unpaired() {
        assert_eq!(ToeNode::is_unpaired(String::from("br")), true);
    }

    #[test]
    fn is_not_tag_unpaired() {
        assert_eq!(ToeNode::is_unpaired(String::from("div")), false);
    }

    // Node tests
    #[test]
    fn test_creating_node() {
        let root_node = ToeNode::create_node(None);
        assert_eq!(root_node.node_type, NodeTypes::Node);
    }

    #[test]
    fn unpaired_node_to_string() {
        let mut node = ToeNode::create_node(Some(String::from("br")));
        assert_eq!(node.to_string(), "<br />");
    }

    #[test]
    fn paired_childless_node_to_string() {
        let mut node = ToeNode::create_node(Some(String::from("br")));
        assert_eq!(node.to_string(), "<br />");
    }

    #[test]
    fn paired_node_to_string() {
        let mut node = ToeNode::create_node(Some(String::from("div")));
        if let Some(ref mut children) = node.children {
            children.push(ToeNode::create_node(Some(String::from("br"))))
        }
        assert_eq!(node.to_string(), "<div><br /></div>");
    }


    // Root Node tests
    #[test]
    fn test_creating_root_node() {
        let root_node = ToeNode::create_root_node();
        assert_eq!(root_node.node_type, NodeTypes::Root);
    }

    #[test]
    fn root_node_to_string() {
        let mut root_node = ToeNode::create_root_node();
        root_node.attributes.insert(String::from("version"), String::from("1.0"));
        assert_eq!(root_node.to_string(), "<?xml version=\"1.0\" ?>");

        // let a = "a".graphemes(true).collect::<Vec<&str>>();
    }

    // Processing nodes
}
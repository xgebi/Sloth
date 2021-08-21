use std::collections::HashMap;

pub(crate) enum NodeTypes {
    Node,
    Root,
    Processing,
    Directive,
    Text,
    Comment,
}

pub struct ToeNode {
    pub(crate) name: Option<String>,
    pub(crate) node_type: NodeTypes,
    pub(crate) attributes: HashMap<String, String>,
    pub(crate) content: Option<String>,
    // children and parent are dealt through aTree
}

impl ToeNode {
    pub fn create_root_node() -> ToeNode {
        ToeNode{
            name: Some(String::from("xml")),
            node_type: NodeTypes::Root,
            attributes: HashMap::new(),
            content: None
        }
    }

    pub fn create_processing_node() -> ToeNode {
        ToeNode{
            name: Some(String::from("xml")),
            node_type: NodeTypes::Root,
            attributes: HashMap::new(),
            content: None
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
        String::new()
    }

    fn root_node_to_string(&self) -> String {
        String::new()
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

    fn is_unpaired(tag_name: String) -> bool {
        let unpaired_tags = ["base", "br", "meta", "hr", "img", "track", "source", "embed", "col", "input", "link"];
        unpaired_tags.contains(&&*tag_name)
    }

    fn is_always_paired(tag_name: String) -> bool {
        let paired_tags = ["script"];
        paired_tags.contains(&&*tag_name)
    }
}

#[cfg(test)]
mod tests {
    use crate::ToeNode;

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
}
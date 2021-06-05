pub mod nodes {
    use std::collections::HashMap;
    use std::rc::Rc;

    #[derive(PartialEq)]
    pub enum NodeTypes {
        NODE,
        ROOT,
        PROCESSING,
        DIRECTIVE,
        TEXT,
        COMMENT
    }

    pub struct Node {
        node_type: NodeTypes,
        html: bool,
        name: Option<String>,
        attributes: Option<HashMap<String, String>>,
        children: Option<Rc<Vec<Node>>>,
        paired_tag: Option<bool>,
        parent: Box<Option<Node>>,
        content: Option<String>,
        cdata: bool
    }

    impl Node {
        pub fn new(node_type: NodeTypes, name: Option<String>, attributes: Option<HashMap<String, String>>, children: Option<Vec<Node>>, paired_tag: Option<bool>, parent: Option<Node>, cdata: bool) -> Node {
            if node_type == NodeTypes::ROOT {
                return Node {
                    node_type: NodeTypes::ROOT,
                    html: true,
                    name: name,
                    attributes: attributes,
                    children: Some(Rc::new(children.unwrap())),
                    paired_tag: Some(paired_tag.unwrap()),
                    parent: Box::new(None),
                    content: None,
                    cdata: false
                };
            }

            if node_type == NodeTypes::TEXT {
                return Node {
                    node_type: NodeTypes::TEXT,
                    html: true,
                    name: None,
                    attributes: None,
                    children: None,
                    paired_tag: Some(false),
                    parent: Box::new(parent),
                    content: None,
                    cdata: cdata
                };
            }

            if node_type == NodeTypes::COMMENT {
                return Node {
                    node_type: NodeTypes::COMMENT,
                    html: true,
                    name: None,
                    attributes: None,
                    children: None,
                    paired_tag: Some(false),
                    parent: Box::new(parent),
                    content: None,
                    cdata: false
                };
            }

            if node_type == NodeTypes::DIRECTIVE {
                return Node {
                    node_type: NodeTypes::DIRECTIVE,
                    html: true,
                    name: None,
                    attributes: attributes,
                    children: None,
                    paired_tag: Some(false),
                    parent: Box::new(parent),
                    content: None,
                    cdata: false
                };
            }

            Node {
                node_type: NodeTypes::NODE,
                html: true,
                name: name,
                attributes: attributes,
                children: Some(Rc::new(children.unwrap())),
                paired_tag: Some(paired_tag.unwrap()),
                parent: Box::new(parent),
                content: None,
                cdata: false
            }
        }

        fn to_html_string(&self) -> String {
            if self.node_type == NodeTypes::ROOT {
                return self.root_node_to_html_string();
            }
            if self.node_type == NodeTypes::TEXT {
                return self.text_node_to_html_string();
            }
            "".to_string()
        }

        fn root_node_to_html_string(&self) -> String {
            "".to_string()
        }

        fn text_node_to_html_string(&self) -> String {
            format!("{}\n", self.content.as_ref().unwrap().as_str()).to_string()
        }

        fn comment_node_to_html_string(&self) -> String {
            format!("<!--{}-->\n", self.content.as_ref().unwrap().as_str()).to_string()
        }

        fn directive_node_to_html_string(&self) -> String {
            let mut result: String = format!("<!{}", self.name.as_ref().unwrap().as_str());

            for (key, val) in self.attributes.as_ref().unwrap().iter() {
                result += format!(" {}=\"{}\"", key, val).as_str()
            }

            result.to_string()
        }
    }
}
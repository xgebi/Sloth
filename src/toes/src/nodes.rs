pub mod nodes {
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
        nodeType: NodeTypes,
        html: bool,
        name: Optional<String>,
        attributes: Optional<HashMap<String, String>>,
        children: Optional<Vec<Node>>,
        pairedTag: Option<bool>,
        parent: Option<Node>,
        content: Option<String>,
        cdata: bool
    }

    impl Node {
        pub fn new(nodeType: NodeTypes, name: Option<String>, attributes: Option<HashMap<String, String>>, children: Option<Vec<Node>>, pairedTag: Option<bool>, parent: Option<Node>) -> Node {
            if nodeType == NodeTypes::ROOT {
                return Node {
                    nodeType: NodeTypes::ROOT,
                    html: true,
                    name: name,
                    attributes: attributes,
                    children: children,
                    pairedTag: pairedTag,
                    parent: None,
                    content: None,
                    cdata: false
                };
            }

            if nodeType == NodeTypes::ROOT {
                return Node {
                    nodeType: NodeTypes::ROOT,
                    html: true,
                    name: name,
                    attributes: attributes,
                    children: children,
                    pairedTag: pairedTag,
                    parent: None,
                    content: None,
                    cdata: false
                };
            }

            if nodeType == NodeTypes::TEXT {
                return Node {
                    nodeType: NodeTypes::TEXT,
                    html: true,
                    name: None,
                    attributes: None,
                    children: None,
                    pairedTag: false,
                    parent: parent,
                    content: None,
                    cdata: cdata
                };
            }

            if nodeType == NodeTypes::COMMENT {
                return Node {
                    nodeType: NodeTypes::COMMENT,
                    html: true,
                    name: None,
                    attributes: None,
                    children: None,
                    pairedTag: false,
                    parent: parent,
                    content: None,
                    cdata: false
                };
            }

            if nodeType == NodeTypes::DIRECTIVE {
                return Node {
                    nodeType: NodeTypes::DIRECTIVE,
                    html: true,
                    name: "",
                    attributes: attributes,
                    children: None,
                    pairedTag: false,
                    parent: parent,
                    content: None,
                    cdata: false
                };
            }

            Node {
                nodeType: NodeTypes::NODE,
                html: true,
                name: name,
                attributes: attributes,
                children: children,
                pairedTag: pairedTag,
                parent: parent,
                content: None,
                cdata: false
            }
        }

        fn toHtmlString(&self) -> String {
            if self.nodeType == NodeTypes::ROOT {
                return self.rootNodeToHtmlString();
            }
            if self.nodeType == NodeTypes::TEXT {
                return self.textNodeToHtmlString();
            }
            "".to_string()
        }

        fn rootNodeToHtmlString(&self) -> String {
            "".to_string()
        }

        fn textNodeToHtmlString(&self) -> String {
            format!("{}\n", self.content.unwrap().as_str()).to_string()
        }

        fn commentNodeToHtmlString(&self) -> String {
            format!("<!--{}-->\n", self.content.unwrap().as_str()).to_string()
        }

        fn directiveNodeToHtmlString(&self) -> String {
            let mut result: String = format!("<!{}", self.name);
            for (attrName, attrValue) in &self.attributes {
                result += format!(" {}=\"{}\"", attrName, attrValue)
            }
            result.to_string()
        }
    }
}
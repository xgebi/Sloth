pub mod nodes {
    enum NodeTypes {
        NODE,
        ROOT,
        PROCESSING,
        DIRECTIVE,
        TEXT,
        COMMENT
    }

    pub struct Node {
        nodeType: String,
        html: bool,
        name: Optional<String>,
        attributes: Optional<HashMap<String, String>>,
        children: Optional<Vec<Node>>,
        pairedTag: bool,
        parent: Option<Node>,
        content: Option<String>,
        cdata: bool
    }

    impl Node {
        fn new(nodeType: NodeTypes, name: Option<String>, attributes: Option<HashMap<String, String>>, children: Option<Vec<Node>>, pairedTag: Option<bool>, parent: Option<Node>) -> Node {
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
            if (self.nodeType == NodeTypes::ROOT) {
                return self.rootNodeToHtmlString();
            }
            ""
        }

        fn rootNodeToHtmlString(&self) -> String {
            ""
        }
    }

    impl RootNode for Node {
        fn new(name: String, attributes: HashMap<String, String>, children: Vec<Node>, pairedTag: bool) -> Node {
            Node {
                nodeType: NodeTypes::ROOT,
                html: true,
                name: name,
                attributes: attributes,
                children: children,
                pairedTag: pairedTag,
                parent: None,
                content: None,
                cdata: false
            }
        }

        fn toHtmlString() -> String {
            ""
        }
    }

    impl TextNode for Node {
        fn new(parent: Node, cdata: bool) -> Node {
            Node {
                nodeType: NodeTypes::TEXT,
                html: true,
                name: None,
                attributes: None,
                children: None,
                pairedTag: false,
                parent: parent,
                content: "",
                cdata: cdata
            }
        }

        fn toHtmlString(&self) -> String {
            format!("{}\n", self.content.unwrap())
        }
    }

    impl CommentNode for Node {
        fn new(parent: Node, content: String) -> Node {
            Node {
                nodeType: NodeTypes::COMMENT,
                html: true,
                name: None,
                attributes: None,
                children: None,
                pairedTag: false,
                parent: parent,
                content: None,
                cdata: false
            }
        }

        fn toHtmlString(&self) -> String {
            format!("<!--{}-->\n", self.content.unwrap())
        }
    }

    impl DirectiveNode for Node {
        fn new(attributes: HashMap<String, String>, parent: Node) -> Node {
            Node {
                nodeType: NodeTypes::DIRECTIVE,
                html: true,
                name: "",
                attributes: attributes,
                children: None,
                pairedTag: false,
                parent: parent,
                content: None,
                cdata: false
            }
        }

        fn toHtmlString(&self) -> String {
            let mut result: String = format!("<!{}", self.name);
            for (attrName, attrValue) in &self.attributes {
                result += format!(" {}=\"{}\"", attrName, attrValue)
            }
            result
        }
    }
}
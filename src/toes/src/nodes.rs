mod nodes {
    enum NodeTypes {
        NODE,
        ROOT,
        PROCESSING,
        DIRECTIVE,
        TEXT,
        COMMENT,
        CDATA_TEXT
    }

    struct Node {
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
        fn new(name: String, attributes: HashMap<String, String>, children: Vec<Node>, pairedTag: bool, parent: Node) -> Node {
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
    }

    impl TextNode for Node {
        fn new(attributes: HashMap<String, String>, children: Vec<Node>, pairedTag: bool, parent: Node, cdata: bool) -> Node {
            Node {
                nodeType: NodeTypes::ROOT,
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
    }

    impl CommentNode for Node {
        fn new(parent: Node, content: String) -> Node {
            Node {
                nodeType: NodeTypes::ROOT,
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
    }

    impl DirectiveNode for Node {
        fn new(attributes: HashMap<String, String>, parent: Node) -> Node {
            Node {
                nodeType: NodeTypes::ROOT,
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
    }
}
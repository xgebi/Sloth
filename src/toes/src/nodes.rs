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
        name: String,
        attributes: HashMap<String, String>,
        children: Vec<Node>,
        pairedTag: bool,
        parent: Option<Node>
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
                parent: parent
            }
        }
    }

    impl RootNode for Node {
        fn new(name: String, attributes: HashMap<String, String>, children: Vec<Node>, pairedTag: bool, parent: Node) -> Node {
            Node {
                nodeType: NodeTypes::ROOT,
                html: true,
                name: name,
                attributes: attributes,
                children: children,
                pairedTag: pairedTag,
                parent: None
            }
        }
    }
}
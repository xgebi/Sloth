use pgs_common::node::{Node, NodeType};

pub(crate) fn compile_node_tree(root_node: Node) -> Node {
    let mut compiled_root_node = Node::create_node(None, Some(NodeType::Root));

    for child in root_node.children {
        compiled_root_node.children.push(compile_node(child))
    }

    compiled_root_node
}

fn compile_node(n: Node) -> Node {
    
    // 1. check if it's a toe's meta node
    // 2. check attributes for toe's attributes

    Node::create_node(None, None)
}
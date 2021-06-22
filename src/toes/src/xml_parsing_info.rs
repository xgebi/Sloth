pub mod xml_parsing_info {
    use crate::nodes::nodes::Node;

    #[derive(PartialEq)]
    pub enum States {
        NEW_PAGE,
        READ_NODE_NAME,
        LOOKING_FOR_ATTRIBUTE,
        LOOKING_FOR_CHILD_NODES,
        INSIDE_SCRIPTS
    }

    pub struct XmlParsingInfo<'a> {
        pub index: u16,
        pub state: States,
        pub current_node: Node<'a>,
        pub root_node: Node<'a>
    }

    impl XmlParsingInfo<'_> {
        fn move_index(mut self, step: Option<u16>) {
            match step {
                None => self.index += 1,
                Some(i) => self.index += i,
            }
        }
    }

}

#[cfg(test)]
mod xml_parsing_info_tests {
    use crate::xml_parsing_info::xml_parsing_info::XmlParsingInfo;
    use crate::xml_parsing_info::xml_parsing_info::States::NEW_PAGE;
    use crate::nodes::nodes::{Node, NodeTypes};
    use std::collections::HashMap;

    #[test]
    fn it_works() {
        let root_node = Node::new(NodeTypes::ROOT, None, Some(HashMap::new()), Some(Vec::new()), Some(false), None, false);
        let xml_parsing_info = XmlParsingInfo{index: 0, state: NEW_PAGE, current_node: &root_node, root_node: &root_node};
    }
}
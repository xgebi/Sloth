use std::collections::HashMap;

use crate::node::Node;
use crate::node_type::NodeType;
use crate::variable_scope::VariableScope;

pub(crate) fn process_toe_import(url_to_import: String, variable_scope: VariableScope, config: HashMap<String, String>) -> Node {
    let theme_path = config.get("theme_path");
    if theme_path.is_some() {
        // process nodes with scan
        // compile the template
    }
    Node {
        name: "".to_string(),
        attributes: Default::default(),
        children: vec![],
        node_type: NodeType::Text,
        text_content: "".to_string(),
    }
}

pub(crate) fn process_toe_fragment(variable_scope: VariableScope, config: HashMap<String, String>) -> Vec<Node> {
    vec![]
}

pub(crate) fn process_toe_if(variable_scope: VariableScope, config: HashMap<String, String>) -> Option<Node> {
    None
}

pub(crate) fn process_toe_for(variable_scope: VariableScope, config: HashMap<String, String>) -> Vec<Node> {
    vec![]
}

pub(crate) fn process_text_content(content: String, variable_scope: VariableScope, should_sanitize: bool) -> String {
    content
}

#[cfg(test)]
mod process_text_content_tests {
    use crate::toe_commands::process_text_content;
    use crate::variable_scope::VariableScope;

    #[test]
    fn test_plain_string_unsanitized() {
        let vs = VariableScope::create();
        let content = "'abc'".to_string();
        let result = process_text_content(content.clone(), vs, false);
        assert_eq!(result, content);
    }
    
    #[test]
    fn test_variable_unsanitized() {
        
    }
    
    #[test]
    fn test_variable_string_unsanitized() {
        
    }
    
    #[test]
    fn test_string_variable_string_unsanitized() {
        
    }
    
    #[test]
    fn test_variable_string_variable_unsanitized() {
        
    }
    
    // TODO add sanitized versions
}
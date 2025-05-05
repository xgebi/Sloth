use std::collections::HashMap;
use unicode_segmentation::UnicodeSegmentation;
use crate::conditions::{resolve_condition_tree, scan_condition};
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

pub(crate) fn process_toe_fragment(node: Node, variable_scope: VariableScope, config: HashMap<String, String>) -> Vec<Node> {
    // check for toe:if
    // check for toe:for
    vec![]
}

pub(crate) fn process_toe_if(node: Node, variable_scope: VariableScope, config: HashMap<String, String>) -> Option<Node> {
    let if_condition = node.attributes.get("toe:if").unwrap().to_string();
    let condition_tree = scan_condition(if_condition);
    let result = resolve_condition_tree(condition_tree, variable_scope);
    if result {
        let mut new_node = node.clone();
        new_node.attributes.remove("toe:if");
        Some(new_node)
    } else {
        None
    }
}

pub(crate) fn process_toe_for(node: Node, variable_scope: VariableScope, config: HashMap<String, String>) -> Vec<Node> {
    vec![]
}

pub(crate) fn process_text_content(content: String, variable_scope: VariableScope, should_sanitize: bool) -> String {
    let mut result = String::new();
    let content_arr = content.graphemes(true).collect::<Vec<&str>>();
    let mut idx = 0;
    let mut quote = String::new();
    let mut current_string = String::new();
    while idx < content_arr.len() {
        if content_arr[idx] == "'" || content_arr[idx] == "'" || content_arr[idx] == "`" {
            if quote.is_empty() {
                quote = content_arr[idx].to_string();
                if !current_string.is_empty() {
                    result.push_str(current_string.as_str());
                }
                current_string = String::new();
            } else if quote == content_arr[idx] {
                quote = String::new();
                result.push_str(current_string.as_str());
                current_string = String::new();
            } else if quote != content_arr[idx].to_string() {
                current_string.push_str(content_arr[idx]);
            }
        } else {
            if quote.is_empty() && !current_string.is_empty() && (content_arr[idx] == " " || idx + 1 == content_arr.len()) {
                if idx + 1 == content_arr.len() {
                    current_string.push_str(content_arr[idx]);
                }
                if variable_scope.clone().variable_exists(&current_string.clone()) {
                    let resolved_option = variable_scope.clone().find_variable(current_string.clone());
                    let resolved = resolved_option.unwrap().to_string();
                    result.push_str(resolved.as_str());
                    current_string = String::new();
                }
            } else {
                if !(content_arr[idx] == " " && quote.is_empty()) {
                    current_string.push_str(content_arr[idx]);
                }
            }
        }
        idx += 1;
    }
    if !current_string.trim().is_empty() {
        result.push_str(current_string.as_str());
    }
    if should_sanitize {
        let mut sanitized = String::new();
        html_escape::encode_safe_to_string(result, &mut sanitized);
        return sanitized;
    }
    result
}

#[cfg(test)]
mod process_text_content_tests {
    use crate::data_type::DataType;
    use crate::toe_commands::process_text_content;
    use crate::variable_scope::VariableScope;

    #[test]
    fn test_plain_string_unsanitized() {
        let vs = VariableScope::create();
        let content = "'abc'".to_string();
        let result = process_text_content(content.clone(), vs, false);
        assert_eq!(result, "abc");
    }

    #[test]
    fn test_variable_unsanitized() {
        let mut vs = VariableScope::create();
        vs.create_variable("abc".to_string(), DataType::String("three".to_string()));
        let content = "abc".to_string();
        let result = process_text_content(content.clone(), vs, false);
        assert_eq!(result, "three");
    }

    #[test]
    fn test_variable_string_unsanitized() {
        let mut vs = VariableScope::create();
        vs.create_variable("abc".to_string(), DataType::String("three".to_string()));
        let content = "abc ' things'".to_string();
        let result = process_text_content(content.clone(), vs, false);
        assert_eq!(result, "three things");
    }

    #[test]
    fn test_string_variable_string_unsanitized() {
        let mut vs = VariableScope::create();
        vs.create_variable("abc".to_string(), DataType::String("three".to_string()));
        let content = "'my ' abc ' things'".to_string();
        let result = process_text_content(content.clone(), vs, false);
        assert_eq!(result, "my three things");
    }

    #[test]
    fn test_variable_string_variable_unsanitized() {
        let mut vs = VariableScope::create();
        vs.create_variable("abc".to_string(), DataType::String("three".to_string()));
        let content = "abc ' of ' abc".to_string();
        let result = process_text_content(content.clone(), vs, false);
        assert_eq!(result, "three of three");
    }

    #[test]
    fn test_plain_string_sanitized() {
        let vs = VariableScope::create();
        let content = "'<abc>'".to_string();
        let result = process_text_content(content.clone(), vs, true);
        assert_eq!(result, "&lt;abc&gt;");
    }
}
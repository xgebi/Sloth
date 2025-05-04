use unicode_segmentation::UnicodeSegmentation;
use crate::data_type::DataType;
use crate::variable_scope::VariableScope;

#[derive(PartialEq, Debug)]
pub(crate) enum ConditionJoints {
    None,
    And,
    Or
}

#[derive(PartialEq, Debug)]
pub(crate) enum ConditionComparison {
    None,
    Eq,
    Neq,
    Lt,
    Lte,
    Gt,
    Gte
}

#[derive(Debug)]
pub(crate) struct ConditionTree {
    pub(crate) content: Vec<DataType>,
    pub(crate) is_resolved: bool,
    pub(crate) unresolved_content: Vec<String>,
    pub(crate) condition_joints: ConditionJoints,
    pub(crate) children: Vec<ConditionTree>,
    pub(crate) condition_comparison: ConditionComparison,
}

impl ConditionTree {
    pub(crate) fn create() -> ConditionTree {
        ConditionTree {
            content: vec![],
            is_resolved: false,
            unresolved_content: vec![],
            condition_joints: ConditionJoints::None,
            children: vec![],
            condition_comparison: ConditionComparison::None,
        }
    }
}

pub(crate) fn scan_condition(cond_str: String) -> ConditionTree {
    let mut cond = ConditionTree {
        content: vec![],
        is_resolved: false,
        unresolved_content: vec![],
        condition_joints: ConditionJoints::None,
        children: vec![],
        condition_comparison: ConditionComparison::None,
    };
    if cond_str.len() == 0 {
        return cond;
    }
    let mut current_word = String::new();
    let mut i = 0;
    let mut is_space_in_quote = false;
    let mut quotation_mark: String = String::new();
    let cond_graphemes = cond_str.graphemes(true).collect::<Vec<&str>>();
    while i < cond_graphemes.len() {
        if cond_graphemes[i] != " " {
            current_word.push_str(cond_graphemes[i]);
            if is_space_in_quote {
                if cond_graphemes[i] == quotation_mark {
                    is_space_in_quote = false;
                    quotation_mark = String::new();
                }
            } else if cond_graphemes[i] == "'" ||
                cond_graphemes[i] == "\"" ||
                cond_graphemes[i] == "`" {
                is_space_in_quote = true;
                quotation_mark = cond_graphemes[i].to_string();
            }
            if i + 1 == cond_graphemes.len() {
                cond.unresolved_content.push(current_word.clone());
            }
        } else if (cond_graphemes[i] == " " || i + 1 == cond_graphemes.len()) && current_word.len() > 0 {
            if is_space_in_quote {
                current_word.push_str(cond_graphemes[i]);
            } else {
                match current_word.as_str() {
                    "lt" => {
                        if cond.condition_comparison == ConditionComparison::None {
                            cond.condition_comparison = ConditionComparison::Lt
                        }
                    }
                    "lte" => {
                        if cond.condition_comparison == ConditionComparison::None {
                            cond.condition_comparison = ConditionComparison::Lte
                        }
                    }
                    "gt" => {
                        if cond.condition_comparison == ConditionComparison::None {
                            cond.condition_comparison = ConditionComparison::Gt
                        }
                    }
                    "gte" => {
                        if cond.condition_comparison == ConditionComparison::None {
                            cond.condition_comparison = ConditionComparison::Gte
                        }
                    }
                    "neq" => {
                        if cond.condition_comparison == ConditionComparison::None {
                            cond.condition_comparison = ConditionComparison::Neq
                        }
                    }
                    "eq" => {
                        if cond.condition_comparison == ConditionComparison::None {
                            cond.condition_comparison = ConditionComparison::Eq
                        }
                    }
                    // The issue is not when joints are of the same kind,
                    // the is that when they are of the different kind, precendence must followed
                    "and" => {
                        if cond.condition_joints == ConditionJoints::None {
                            cond.condition_joints = ConditionJoints::And;
                        }
                        if cond.condition_joints == ConditionJoints::Or {}
                    }
                    "or" => {
                        if cond.condition_joints == ConditionJoints::None {
                            cond.condition_joints = ConditionJoints::Or;
                        }
                        if cond.condition_joints == ConditionJoints::And {}
                    }
                    &_ => {
                        cond.unresolved_content.push(current_word.clone());
                    }
                }
                current_word = String::new();
            }
        }
        i += 1;
    }
    cond
}

pub(crate) fn resolve_condition_tree(cond_tree: ConditionTree, variable_scope: VariableScope) -> bool {
    println!("{:?}", cond_tree);
    if cond_tree.condition_joints == ConditionJoints::None && cond_tree.condition_comparison == ConditionComparison::None {
        
    }
    false
}

#[cfg(test)]
mod scanning_tests {
    use crate::conditions::{scan_condition, ConditionComparison, ConditionJoints, ConditionTree};

    #[test]
    fn test_creating_condition() {
        let condition = ConditionTree::create();
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), true);
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    
    // Singles
    // DataType::String
    #[test]
    fn test_scanning_empty_string_condition() {
        let condition = scan_condition("''".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "''");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    
    #[test]
    fn test_scanning_double_quote_in_single_string_condition() {
        let condition = scan_condition("'\"'".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "'\"'");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    
    #[test]
    fn test_scanning_double_quote_and_space_in_single_string_condition() {
        let condition = scan_condition("'\" \"'".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "'\" \"'");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    
    // DataType::Nil
    #[test]
    fn test_scanning_empty_condition() {
        let condition = scan_condition("".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), true);
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    
    // DataType::Boolean(false)
    // DataType::Boolean(true)
    #[test]
    fn test_scanning_false_condition() {
        let condition = scan_condition("false".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "false");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    // DataType::Int(0)
    // DataType::Int(1)
    #[test]
    fn test_scanning_numeric_zero_condition() {
        let condition = scan_condition("0".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "0");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    // DataType::Float(0.0)
    // DataType::Float(0.1)
    #[test]
    fn test_scanning_numeric_one_condition() {
        let condition = scan_condition("1.0".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1.0");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    // DataType::Array(Vec::new())
    #[test]
    fn test_scanning_empty_array_condition() {
        let condition = scan_condition("[]".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "[]");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    // DataType::Array(vec![DataType::Nil])
    #[test]
    fn test_scanning_array_condition() {
        let condition = scan_condition("[false]".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "[false]");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    // DataType::HashMap(HashMap::new())
    // DataType::HashMap(hash : DataType::Nil])
    // 
    // One operator
    // x eq y
    #[test]
    fn test_simple_eq_false_condition() {
        let condition = scan_condition("false eq true".to_string());
        println!("{:?}", condition);
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "false");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    
    #[test]
    fn test_simple_eq_true_condition() {
        let condition = scan_condition("false eq false".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "false");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    // x neq y
    #[test]
    fn test_simple_neq_false_condition() {
        let condition = scan_condition("false neq true".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "false");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    
    #[test]
    fn test_simple_neq_true_condition() {
        let condition = scan_condition("false neq false".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "false");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
    }
    // x lt y
    #[test]
    fn test_simple_lt_true_condition() {
        let condition = scan_condition("1 lt 2".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "2");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Lt);
    }
    
    #[test]
    fn test_simple_lt_false_condition() {
        let condition = scan_condition("1 lt 1".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "1");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Lt);
    }
    // x lte y
    #[test]
    fn test_simple_lte_true_condition() {
        let condition = scan_condition("1 lte 2".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "2");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Lte);
    }
    
    #[test]
    fn test_simple_lte_equal_true_condition() {
        let condition = scan_condition("1 lte 1".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "1");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Lte);
    }
    
    #[test]
    fn test_simple_lte_false_condition() {
        let condition = scan_condition("2 lte 1".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "2");
        assert_eq!(condition.unresolved_content[1], "1");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Lte);
    }
    // x gt y
    #[test]
    fn test_simple_gt_true_condition() {
        let condition = scan_condition("1 gt 0".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "0");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Gt);
    }
    
    #[test]
    fn test_simple_gt_false_condition() {
        let condition = scan_condition("1 gt 1".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "1");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Gt);
    }
    // x gte y
    #[test]
    fn test_simple_gte_true_condition() {
        let condition = scan_condition("1 gte 0".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "0");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Gte);
    }
    
    #[test]
    fn test_simple_gte_equal_true_condition() {
        let condition = scan_condition("1 gte 1".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "1");
        assert_eq!(condition.unresolved_content[1], "1");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Gte);
    }
    
    #[test]
    fn test_simple_gte_false_condition() {
        let condition = scan_condition("2 gte 1".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "2");
        assert_eq!(condition.unresolved_content[1], "1");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::None);
        assert_eq!(condition.condition_comparison, ConditionComparison::Gte);
    }
    // 
    // Two operators
    // x and y
    #[test]
    fn test_simple_and_condition() {
        let condition = scan_condition("x and y".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "x");
        assert_eq!(condition.unresolved_content[1], "y");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::And);
        assert_eq!(condition.condition_comparison, ConditionComparison::None);
    }
    // x or y
    #[test]
    fn test_simple_or_condition() {
        let condition = scan_condition("x or y".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "x");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::Or);
        assert_eq!(condition.condition_comparison, ConditionComparison::None);
    }
    // 
    // Three operators
    // x and y and z
    #[test]
    fn test_two_and_conditions() {
        let condition = scan_condition("x and y and z".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "x");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::And);
        assert_eq!(condition.condition_comparison, ConditionComparison::None);
    }
    // x and y or z -> same as x and (y or z)
    // x or y and z -> same as (x or y) and z
    // x or y or z
    #[test]
    fn test_two_or_conditions() {
        let condition = scan_condition("x or y or z".to_string());
        assert_eq!(condition.content.is_empty(), true);
        assert_eq!(condition.is_resolved, false);
        assert_eq!(condition.unresolved_content.is_empty(), false);
        assert_eq!(condition.unresolved_content[0], "x");
        assert_eq!(condition.children.is_empty(), true);
        assert_eq!(condition.condition_joints, ConditionJoints::Or);
        assert_eq!(condition.condition_comparison, ConditionComparison::None);
    }
    
}

#[cfg(test)]
mod resolving_tests {
    use crate::conditions::{resolve_condition_tree, scan_condition, ConditionTree};
    use crate::variable_scope::VariableScope;
    
    // Singles
    // 
    // DataType::Nil
    #[test]
    fn test_scanning_empty_condition() {
        let condition = scan_condition("".to_string());
        let vars = VariableScope::create();
        let result = resolve_condition_tree(condition, vars);
        assert_eq!(result, false);
    }
    // DataType::Boolean(false)
    // DataType::Boolean(true)
    // DataType::Int(0)
    // DataType::Int(1)
    // DataType::Float(0.0)
    // DataType::Float(0.1)
    // DataType::Array(Vec::new())
    // DataType::Array(vec![DataType::Nil])
    // DataType::HashMap(HashMap::new())
    // DataType::HashMap(hash : DataType::Nil])
    // 
    // One operator
    // x eq y
    // x neq y
    // x lt y
    // x lte y
    // x gt y
    // x gte y
    // 
    // Two operators
    // x and y
    // x or y
    // 
    // Three operators
    // x and y and z
    // x and y or z -> same as x and (y or z)
    // x or y and z -> same as (x or y) and z
    // x or y or z
}
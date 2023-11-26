use std::num::ParseIntError;
use std::rc::Rc;
use crate::variable_scope::VariableScope;
use unicode_segmentation::UnicodeSegmentation;
use regex::Regex;

#[cfg(test)]
mod tests {
    use crate::condition_processing::process_condition;
    use crate::variable_scope::VariableScope;
    use std::rc::Rc;

    // compound tests
    // ands
    #[test]
    fn simple_and_without_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 and myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_and_with_partial_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) and myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_and_with_partial_parenthesis_case_two() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 and (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_and_with_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) and (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_and_without_parenthesis_with_first_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not myVar neq 1 and myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_partial_parenthesis_with_first_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not (myVar neq 1) and myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_without_parenthesis_with_second_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 and not myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_partial_parenthesis_with_second_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) and not myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_partial_parenthesis_with_second_not_type_two() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 and not (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_parenthesis_with_second_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) and not (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_without_parenthesis_double_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not myVar neq 1 and not myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_parenthesis_after_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not (myVar neq 1 and myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_parenthesis_first_not_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(not (myVar neq 1)) and myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_parenthesis_with_second_not_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) and (not (myVar neq 3))".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_and_with_parenthesis_with_double_not_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(not (myVar neq 1)) and (not (myVar neq 3))".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    // ors
    #[test]
    fn simple_or_and_without_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 or myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_partial_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) or myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_partial_parenthesis_case_two() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 or (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) or (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_without_parenthesis_with_first_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not myVar neq 1 or myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_partial_parenthesis_with_first_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not (myVar neq 1) or myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_and_with_parenthesis_with_first_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not (myVar neq 1) or (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_without_parenthesis_with_second_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 or not myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_partial_parenthesis_with_second_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) or not myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_partial_parenthesis_with_second_not_type_two() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 or not (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_parenthesis_with_second_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) or not (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_without_parenthesis_double_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not myVar neq 1 or not myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_or_with_parenthesis_after_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("not (myVar neq 1 or myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn simple_or_with_partial_parenthesis_first_not_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(not (myVar neq 1)) or myVar neq 3".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_parenthesis_first_not() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(not (myVar neq 1)) or (myVar neq 3)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_parenthesis_with_second_not_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1) or (not (myVar neq 3))".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn simple_or_with_parenthesis_with_double_not_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(not (myVar neq 1)) or (not (myVar neq 3))".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    // mix
    #[test]
    fn and_or_without_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 and myVar neq 2 or myVar neq 0".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn and_with_parenthesis_or() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1 and myVar neq 2) or myVar neq 0".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn and_or_with_partial_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("myVar neq 1 and (myVar neq 2 or myVar neq 0)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn and_or_with_parenthesis() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1 or myVar neq 2) and (myVar neq 0 or myVar neq 2)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn and_or_with_parenthesis_with_parenthesis_nots() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"2".to_string());
        let res = process_condition("(myVar neq 1 or not myVar neq 2) and (myVar neq 0 or not myVar neq 2)".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }
}
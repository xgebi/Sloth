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

    #[test]
    fn condition_is_true() {
        let var_scope = VariableScope::create();
        let res = process_condition("true".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn condition_is_false() {
        let var_scope = VariableScope::create();
        let res = process_condition("false".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    // simple conditions
    #[test]
    fn bool_variable() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"true".to_string());
        let res = process_condition("myVar".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn variable_compare_lte() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar lte 1".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn variable_compare_not_lte() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar lte 0".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn variable_compare_lt() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar lt 2".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn variable_compare_not_lt() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar lt 1".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn variable_compare_gte() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar gte 1".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn variable_compare_not_gte() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar gte 2".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn variable_compare_gt() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar gt 2".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn variable_compare_not_gt() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar gt 1".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn variable_compare_eq() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar eq 1".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn variable_compare_not_eq() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar eq 2".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

    #[test]
    fn variable_compare_neq() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar neq 2".to_string(), Rc::new(var_scope));
        assert_eq!(res, true);
    }

    #[test]
    fn variable_compare_not_neq() {
        let mut var_scope = VariableScope::create();
        var_scope.create_variable(&"myVar".to_string(), &"1".to_string());
        let res = process_condition("myVar neq 1".to_string(), Rc::new(var_scope));
        assert_eq!(res, false);
    }

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
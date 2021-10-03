use std::rc::Rc;
use crate::variable_scope::VariableScope;
use mockall::*;
use regex::Regex;

pub(crate) struct Regexes {
    int_re: Regex,
    float_re: Regex,
    single_str: Regex,
    double_str: Regex,
}

impl Regexes {
    pub(crate) fn new() -> Regexes {
        Regexes {
            int_re: Regex::new(r"^\d+$").unwrap(),
            float_re: Regex::new(r"^\d+[\.,]\d+$").unwrap(),
            single_str: Regex::new(r"^'.+'$").unwrap(),
            double_str: Regex::new(r#"^".+"$"#).unwrap(),
        }
    }
}

pub(crate) struct SimpleCondition {
    pub(crate) negated: bool,
    pub(crate) lhs: String,
    pub(crate) rhs: String,
    pub(crate) operator: String,
}

#[automock]
impl SimpleCondition {
    pub(crate) fn new_from_lhs(lhs: String) -> SimpleCondition {
        SimpleCondition {
            lhs,
            rhs: String::new(),
            operator: String::new(),
            negated: false
        }
    }

    pub(crate) fn new_from_negation(negated: bool) -> SimpleCondition {
        SimpleCondition {
            lhs: String::new(),
            rhs: String::new(),
            operator: String::new(),
            negated
        }
    }

    pub(crate) fn evaluate(&self, variable_scope: Rc<VariableScope>) -> bool {
        let regs = Regexes::new();
        let lhs = &self.lhs.clone();

        if self.lhs == "true" {
            self.evaluate_after_boolean(true, variable_scope)
        } else if self.lhs == "false" {
            self.evaluate_after_boolean(false, variable_scope)
        } else if regs.int_re.is_match(lhs.as_str()) {
            self.evaluate_after_int(&lhs.parse::<i64>().unwrap(), variable_scope)
        } else if regs.float_re.is_match(lhs.as_str()) {
            self::SimpleCondition::evaluate_after_float(&lhs.parse::<f64>().unwrap(), variable_scope)
        } else if regs.single_str.is_match(lhs.as_str()) {
            let substring: &str = &lhs[1..lhs.len() - 1];
            self::SimpleCondition::evaluate_after_string(String::from(substring), variable_scope)
        } else if regs.double_str.is_match(lhs.as_str()) {
            let substring: &str = &self.lhs[1..lhs.len() - 1];
            self::SimpleCondition::evaluate_after_string(String::from(substring), variable_scope)
        } else {
            self::SimpleCondition::evaluate_lhs_variable(variable_scope)
        }
    }

    fn evaluate_after_int(&self, resolved_lhs: &i64, variable_scope: Rc<VariableScope>) -> bool {
        false
    }

    fn evaluate_after_float(resolved_lhs: &f64, variable_scope: Rc<VariableScope>) -> bool {
        false
    }

    fn evaluate_after_string(resolved_lhs: String, variable_scope: Rc<VariableScope>) -> bool {
        false
    }

    fn evaluate_after_boolean(&self, resolved_lhs: bool, variable_scope: Rc<VariableScope>) -> bool {
        false
    }

    fn evaluate_lhs_variable(variable_scope: Rc<VariableScope>) -> bool {
        false
    }

    fn evaluate_int_int(resolved_lhs: i64, resolved_rhs: i64) -> bool {
        false
    }

    fn evaluate_int_float(resolved_lhs: i64, resolved_rhs: f64) -> bool {
        false
    }

    fn evaluate_int_string(resolved_lhs: i64, resolved_rhs: String) -> bool {
        false
    }

    fn evaluate_int_bool(resolved_lhs: i64, resolved_rhs: bool) -> bool {
        false
    }

    fn evaluate_float_int(resolved_lhs: f64, resolved_rhs: i64) -> bool {
        false
    }

    fn evaluate_float_float(resolved_lhs: f64, resolved_rhs: f64) -> bool {
        false
    }

    fn evaluate_float_string(resolved_lhs: f64, resolved_rhs: String) -> bool {
        false
    }

    fn evaluate_float_bool(resolved_lhs: f64, resolved_rhs: bool) -> bool {
        false
    }

    fn evaluate_string_int(resolved_lhs: String, resolved_rhs: i64) -> bool {
        false
    }

    fn evaluate_string_float(resolved_lhs: String, resolved_rhs: f64) -> bool {
        false
    }

    fn evaluate_string_string(resolved_lhs: String, resolved_rhs: String) -> bool {
        false
    }

    fn evaluate_string_bool(resolved_lhs: String, resolved_rhs: bool) -> bool {
        false
    }

    fn evaluate_bool_int(resolved_lhs: bool, resolved_rhs: i64) -> bool {
        false
    }

    fn evaluate_bool_float(resolved_lhs: bool, resolved_rhs: f64) -> bool {
        false
    }

    fn evaluate_bool_string(resolved_lhs: bool, resolved_rhs: String) -> bool {
        false
    }

    fn evaluate_bool_bool(&self, resolved_lhs: bool, resolved_rhs: bool) -> bool {
        let eq = String::from("eq");
        let ne = String::from("ne");
        if self.operator == eq {
            if !self.negated {
                return resolved_lhs == resolved_rhs;
            }
            resolved_lhs != resolved_rhs
        } else if self.operator == ne {
            if !self.negated {
                return resolved_lhs != resolved_rhs;
            }
            resolved_lhs == resolved_rhs
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::simple_condition::SimpleCondition;

    #[test]
    fn test_bool_equals_bool() {
        let cond = SimpleCondition {
            negated: false,
            lhs: "true".to_string(),
            rhs: "true".to_string(),
            operator: "eq".to_string()
        };
        assert_eq!(cond.evaluate_bool_bool(true, true), true);
    }

    #[test]
    fn test_negated_bool_equals_bool() {
        let cond = SimpleCondition {
            negated: true,
            lhs: "true".to_string(),
            rhs: "true".to_string(),
            operator: "eq".to_string()
        };
        assert_eq!(cond.evaluate_bool_bool(true, true), false);
    }

    #[test]
    fn test_bool_not_equals_bool() {
        let cond = SimpleCondition {
            negated: false,
            lhs: "true".to_string(),
            rhs: "true".to_string(),
            operator: "ne".to_string()
        };
        assert_eq!(cond.evaluate_bool_bool(true, true), false);
    }

    #[test]
    fn test_negated_bool_not_equals_bool() {
        let cond = SimpleCondition {
            negated: true,
            lhs: "true".to_string(),
            rhs: "true".to_string(),
            operator: "ne".to_string()
        };
        assert_eq!(cond.evaluate_bool_bool(true, true), true);
    }
}

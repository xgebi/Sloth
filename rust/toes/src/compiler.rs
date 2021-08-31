use std::rc::Rc;
use crate::variable_scope::VariableScope;

fn process_condition(condition: String, variable_scope: Rc<VariableScope>) -> bool {
    if condition.to_lowercase() == "true" {
        return true;
    } else if condition.to_lowercase() == "false" {
        return false;
    }

    false
}

#[cfg(test)]
mod tests {
    use crate::compiler::process_condition;
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
}
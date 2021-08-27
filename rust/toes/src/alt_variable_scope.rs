use std::collections::HashMap;
use std::rc::Rc;

#[derive(Clone)]
struct SingleScope {
    variables: HashMap<String, String>
}

#[derive(Clone)]
struct VariableScopeA {
    scopes: Vec<SingleScope>
}

impl VariableScopeA {
    fn find_variable(self, variable_name: &String) -> Option<String> {
        for scope in self.scopes.iter().rev() {
            if scope.variables.contains_key(variable_name) {
                return Some(scope.variables.get(variable_name).unwrap().clone())
            }
        }
        return None
    }

    fn is_variable(self, variable_name: &String) -> bool {
        false
    }

    fn create_variable(self, variable_name: &String) -> bool {
        false
    }

    fn assign_variable(self, variable_name: &String) -> bool {
        false
    }
}

#[cfg(test)]
mod tests {
    use crate::alt_variable_scope::{VariableScopeA, SingleScope};
    use std::collections::HashMap;

    #[test]
    fn test_creating_scope() {
        let scope = VariableScopeA {
            scopes: Vec::new()
        };
        assert_eq!(scope.scopes.len(), 0);
    }

    #[test]
    fn test_creating_scope_with_single_scope() {
        let mut scope = VariableScopeA {
            scopes: Vec::new()
        };

        let single_scope = SingleScope {
            variables: HashMap::new()
        };

        scope.scopes.push(single_scope);

        assert_eq!(scope.scopes.len(), 1)
    }

    #[test]
    fn test_find_variable_in_current_scope() {
        let mut scope = VariableScopeA {
            scopes: Vec::new()
        };
        let mut ss = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss);

        let last = scope.scopes.len().clone() - 1;
        &scope.scopes[last].variables.insert(String::from("var"), String::from("a"));

        assert_eq!(scope.find_variable(&String::from("var")).unwrap(), String::from("a"));
    }

    #[test]
    fn test_find_variable_in_parent_scope() {
        let mut scope = VariableScopeA {
            scopes: Vec::new()
        };
        let mut ss1 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss1);

        let last = scope.scopes.len().clone() - 1;
        &scope.scopes[last].variables.insert(String::from("var"), String::from("a"));

        let mut ss2 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss2);

        assert_eq!(scope.find_variable(&String::from("var")).unwrap(), String::from("a"));
    }
}
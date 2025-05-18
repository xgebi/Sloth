use std::collections::HashMap;
use std::fmt::{Display};
use std::rc::Rc;
use pgs_common::value::Value;

#[derive(Clone, Debug)]
struct SingleScope {
    variables: HashMap<String, Rc<Value>>
}

#[derive(Clone, Debug)]
pub(crate) struct VariableScope {
    scopes: Vec<SingleScope>
}

impl VariableScope {
    pub(crate) fn create() -> VariableScope {
        VariableScope {
            scopes: vec![SingleScope {
                variables: HashMap::new(),
            }],
        }
    }

    pub(crate) fn create_from_hashmap(hm: HashMap<String, Rc<Value>>) -> VariableScope {
        let mut scopes = vec![SingleScope {
            variables: hm,
        }];
        VariableScope {
            scopes,
        }
    }

    pub(crate) fn remove_last_scope(mut self) {
        if self.scopes.len() > 0 {
            self.scopes.pop();
        }
    }

    pub(crate) fn add_new_scope(mut self) -> Self {
        self.scopes.push(SingleScope {
            variables: HashMap::new(),
        });
        self
    }

    pub(crate) fn find_variable(self, variable_name: String) -> Option<Rc<Value>> {
        for scope in self.scopes.iter().rev() {
            if scope.variables.contains_key(variable_name.as_str()) {
                return Some(Rc::clone(&scope.variables.get(variable_name.as_str()).unwrap().clone()))
            }
        }
        None
    }

    pub(crate) fn variable_exists(self, variable_name: &String) -> bool {
        for scope in self.scopes.iter().rev() {
            if scope.variables.contains_key(variable_name) {
                return true;
            }
        }
        false
    }

    pub(crate) fn create_variable(&mut self, variable_name: String, variable_value: Rc<Value>) -> bool {
        if !self.scopes.last().unwrap().variables.contains_key(variable_name.as_str()) {
            let last_index = self.scopes.len() - 1;
            self.scopes[last_index].variables.insert(variable_name.to_string(), Rc::clone(&variable_value));
            return true;
        }

        false
    }

    pub(crate) fn assign_variable(&mut self, variable_name: String, mut variable_value: Rc<Value>) -> bool {
        let mut current_index = self.scopes.len() - 1;
        loop {
            if self.scopes[current_index].variables.contains_key(variable_name.as_str()) {
                if let Some(x) = self.scopes[current_index].variables.get_mut(variable_name.as_str()) {
                    let val = Rc::clone(&variable_value);
                    *x = val;
                }
                return true;
            }
            if current_index == 0 {
                break;
            }
            current_index -= 1;
        }
        false
    }
}

#[cfg(test)]
mod tests {
    use crate::variable_scope::{VariableScope, SingleScope, Value};
    use std::collections::HashMap;
    use std::rc::Rc;

    #[test]
    fn test_creating_scope() {
        let scope = VariableScope::create();
        assert_eq!(scope.scopes.len(), 1);
    }

    #[test]
    fn test_creating_scope_with_single_scope() {
        let mut scope = VariableScope {
            scopes: Vec::new()
        };

        let single_scope = SingleScope {
            variables: HashMap::new()
        };

        scope.scopes.push(single_scope);

        assert_eq!(scope.scopes.len(), 1)
    }

    #[test]
    fn test_creating_scope_from_hm() {
        let hm: HashMap<String, Rc<Value>> = HashMap::new();
        let scope = VariableScope::create_from_hashmap(hm);
        assert_eq!(scope.scopes.len(), 1);
    }

    #[test]
    fn test_find_variable_in_current_scope() {
        let mut scope = VariableScope {
            scopes: Vec::new()
        };
        let mut ss = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss);

        let last = scope.scopes.len().clone() - 1;
        &scope.scopes[last].variables.insert(String::from("var"), Rc::new(Value::String(String::from("a"))));

        let result = scope.find_variable(String::from("var")).unwrap();

        if let Value::String(value) = result.as_ref() {
            assert_eq!(value, "a")
        } else {
            panic!()
        }
    }

    #[test]
    fn test_find_variable_in_parent_scope() {
        let mut scope = VariableScope {
            scopes: Vec::new()
        };
        let mut ss1 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss1);

        let last = scope.scopes.len().clone() - 1;
        &scope.scopes[last].variables.insert(String::from("var"), Rc::new(Value::String(String::from("a"))));

        let mut ss2 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss2);

        let result = scope.find_variable(String::from("var")).unwrap();

        if let Value::String(value) = result.as_ref() {
            assert_eq!(value, "a")
        } else {
            panic!()
        }
    }

    #[test]
    fn test_creating_variable() {
        let mut scope = VariableScope {
            scopes: Vec::new()
        };
        let mut ss1 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss1);

        assert_eq!(scope.create_variable(String::from("var"), Rc::new(Value::String(String::from("a")))), true)
    }

    #[test]
    fn test_creating_variable_twice() {
        let mut scope = VariableScope {
            scopes: Vec::new()
        };
        let mut ss1 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss1);

        assert_eq!(scope.create_variable(String::from("var"), Rc::new(Value::String(String::from("a")))), true);
        assert_eq!(scope.create_variable(String::from("var"), Rc::new(Value::String(String::from("a")))), false);
    }

    #[test]
    fn test_assign_variable() {
        let mut scope = VariableScope {
            scopes: Vec::new()
        };
        let mut ss1 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss1);

        assert_eq!(scope.create_variable(String::from("var"), Rc::new(Value::String(String::from("a")))), true);

        let mut ss2 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss2);

        assert_eq!(scope.assign_variable(String::from("var"), Rc::new(Value::String(String::from("b")))), true);

        let result = scope.find_variable(String::from("var")).unwrap();

        if let Value::String(value) = result.as_ref() {
            assert_eq!(value, "b")
        } else {
            panic!()
        }
    }

    #[test]
    fn test_fail_assign_variable() {
        let mut scope = VariableScope {
            scopes: Vec::new()
        };
        let mut ss1 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss1);

        let mut ss2 = SingleScope {
            variables: HashMap::new()
        };
        scope.scopes.push(ss2);

        assert_eq!(scope.assign_variable(String::from("var"), Rc::new(Value::String(String::from("b")))), false);
    }

    // TODO add different values other than strings
}
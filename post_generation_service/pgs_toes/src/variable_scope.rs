use std::cmp::Ordering;
use std::collections::HashMap;
use std::fmt::{Display, Formatter};
use std::ptr::write;
use std::rc::Rc;

#[derive(Clone, Debug)]
pub(crate) enum Value {
    Boolean(bool),
    Nil,
    Number(f64),
    String(String),
    HashMap(HashMap<String, Rc<Value>>),
    Array(Vec<Rc<Value>>)
}

impl PartialEq for Value {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Value::Boolean(a), Value::Boolean(b)) => a == b,
            (Value::Nil, Value::Nil) => true,
            (Value::Number(a), Value::Number(b)) => a == b,
            (Value::String(a), Value::String(b)) => a == b,
            (Value::Array(a), Value::Array(b)) => {
                if a.len() != b.len() {
                    return false;
                }
                for i in 0..a.len() {
                    if a[i] != b[i] {
                        return false;
                    }
                }
                true
            }
            (Value::HashMap(a), Value::HashMap(b)) => {
                if a.keys().len() != b.keys().len() {
                    return false;
                }
                for i in a.keys() {
                    if b.get(i).is_none() {
                        return false;
                    }
                }
                true
            }
            _ => false,
        }
    }
}

// impl PartialOrd for Value {
//     fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
//         Some(self.cmp(other))
//     }
//
//     fn lt(&self, other: &Self) -> bool {
//         match (self, other) {
//             (Value::Number(a), Value::Number(b)) => a < b,
//             (Value::String(a), Value::String(b)) => a < b,
//             _ => false
//         }
//     }
//
//     fn le(&self, other: &Self) -> bool {
//         match (self, other) {
//             (Value::Number(a), Value::Number(b)) => a <= b,
//             (Value::String(a), Value::String(b)) => a <= b,
//             _ => false
//         }
//     }
//
//     fn gt(&self, other: &Self) -> bool {
//         match (self, other) {
//             (Value::Number(a), Value::Number(b)) => a > b,
//             (Value::String(a), Value::String(b)) => a > b,
//             _ => false
//         }
//     }
//
//     fn ge(&self, other: &Self) -> bool {
//         match (self, other) {
//             (Value::Number(a), Value::Number(b)) => a >= b,
//             (Value::String(a), Value::String(b)) => a >= b,
//             _ => false
//         }
//     }
// }

impl Display for Value {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match (self) {
            Value::Boolean(a) => write!(f, "{}", a.clone()),
            Value::Nil => write!(f, "null"),
            Value::Number(a) => write!(f, "{}", a.clone()),
            Value::String(a) => write!(f, "{}", a.clone()),
            Value::Array(a) => {
                let mut res = String::new();
                for item in a {
                    res += ",";
                    res += item.as_ref().to_string().as_str();
                }
                write!(f, "{}", res)
            }
            Value::HashMap(a) => write!(f, "object"),
            _ => write!(f, "unknown"),
        }
    }
}

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

    pub(crate) fn add_new_scope(mut self) {
        self.scopes.push(SingleScope {
            variables: HashMap::new(),
        })
    }

    pub(crate) fn find_variable(self, variable_name: String) -> Option<Rc<Value>> {
        for scope in self.scopes.iter().rev() {
            if scope.variables.contains_key(variable_name.as_str()) {
                return Some(Rc::clone(&scope.variables.get(variable_name.as_str()).unwrap().clone()))
            }
        }
        return None
    }

    pub(crate) fn variable_exists(self, variable_name: &String) -> bool {
        for scope in self.scopes.iter().rev() {
            if scope.variables.contains_key(variable_name) {
                return true;
            }
        }
        return false;
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
}
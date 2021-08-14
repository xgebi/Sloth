use std::collections::HashMap;

struct VariableScope {
    parent: VariableScope,
    variables: HashMap<String, String>
}

impl VariableScope {
    fn find_variable(name: &String) {

    }

    fn is_variable(name: &String) {

    }

    fn assign_variable(name: &String, value: &String) {

    }

    fn create_variable(name: &String, value: &String) {

    }
}
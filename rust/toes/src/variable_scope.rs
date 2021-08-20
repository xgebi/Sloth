use std::collections::HashMap;
use atree::{Node, Arena};
use std::collections::hash_map::Entry;

struct VariableScope {
    variables: HashMap<String, String>
}

// TODO rework it to arena and token instead of Node
fn find_variable(node: &Node<VariableScope>, arena: &Arena<VariableScope>, variable_name: &String) -> Option<String> {
    if node.data.variables.contains_key(variable_name) {
        return Some(node.data.variables.get(variable_name).unwrap().clone());
    }
    while let parent = node.ancestors(arena).next().unwrap() {
        if parent.data.variables.contains_key(variable_name) {
            return Some(parent.data.variables.get(variable_name).unwrap().clone());
        }
    }
    return None
}

fn is_variable(node: &Node<VariableScope>, arena: &Arena<VariableScope>, variable_name: &String) -> bool {
    if node.data.variables.contains_key(variable_name) {
        return node.data.variables.contains_key(variable_name);
    } else {
        while let parent = node.ancestors(arena).next().unwrap() {
            if parent.data.variables.contains_key(variable_name) {
                return parent.data.variables.contains_key(variable_name);
            }
        }
    }
    return false;
}

fn create_variable(node: &mut Node<VariableScope>, arena: &Arena<VariableScope>, variable_name: String, variable_value: String) -> Result<(), ()> {
    if !node.data.variables.contains_key(&*variable_name) {
        node.data.variables.insert(variable_name, variable_value);
        return Ok(());
    }
    Err(())
}

fn assign_variable(node: &mut Node<VariableScope>, arena: &mut Arena<VariableScope>, variable_name: String, mut variable_value: String) -> Result<(), ()> {
    if node.data.variables.contains_key(&*variable_name) {
        node.data.variables.insert(variable_name, variable_value);
        return Ok(());
    } else {
        while let mut parent = node.ancestors_tokens(arena).next().unwrap() {
            if arena.get(parent).unwrap().data.variables.contains_key(&*variable_name) {
                arena.get_mut(parent).unwrap().data.variables.entry(variable_name).and_modify(|e| { *e = variable_value });
                return Ok(());
            }
        }
    }
    Err(())
}

#[cfg(test)]
mod tests {
    use atree::Arena;
    use crate::variable_scope::{VariableScope, is_variable, find_variable, assign_variable};
    use std::collections::HashMap;

    #[test]
    fn has_variable_in_local_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert("myVar".parse().unwrap(), "'1'".parse().unwrap());
        let (mut arena, root_token) = Arena::with_data(top_scope);

        assert_eq!(is_variable(&arena[root_token], &arena, &String::from("myVar")), true);
    }

    #[test]
    fn find_variable_in_local_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert("myVar".parse().unwrap(), "'1'".parse().unwrap());
        let (mut arena, root_token) = Arena::with_data(top_scope);

        assert_eq!(find_variable(&arena[root_token], &arena, &String::from("myVar")), Some(String::from("'1'")));
    }

    #[test]
    fn assign_variable_not_in_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        let expected = Ok(());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let result = assign_variable(&mut arena[root_token], &mut arena, String::from("myVar"), String::from("'1'"));
        assert_eq!(result, expected);
    }
}
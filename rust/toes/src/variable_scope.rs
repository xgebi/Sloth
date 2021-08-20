use std::collections::HashMap;
use atree::{Node, Arena, Token};
use std::collections::hash_map::Entry;

struct VariableScope {
    variables: HashMap<String, String>
}

fn find_variable(arena: &Arena<VariableScope>, token: Token, variable_name: &String) -> Option<String> {
    if arena.get(token).unwrap().data.variables.contains_key(variable_name) {
        return Some(arena.get(token).unwrap().data.variables.get(variable_name).unwrap().clone());
    }
    for parent in arena.get(token).unwrap().ancestors(arena).next() {
        if parent.data.variables.contains_key(variable_name) {
            return Some(parent.data.variables.get(variable_name).unwrap().clone());
        }
    }
    return None
}

fn is_variable(arena: &Arena<VariableScope>, token: Token, variable_name: &String) -> bool {
    if arena.get(token).unwrap().data.variables.contains_key(variable_name) {
        return arena.get(token).unwrap().data.variables.contains_key(variable_name);
    } else {
        for parent in arena.get(token).unwrap().ancestors(arena).next() {
            if parent.data.variables.contains_key(variable_name) {
                return parent.data.variables.contains_key(variable_name);
            }
        }
    }
    return false;
}

fn create_variable(arena: &mut Arena<VariableScope>, token: Token, variable_name: String, variable_value: String) -> Result<(), ()> {
    if !arena.get(token).unwrap().data.variables.contains_key(&*variable_name) {
        arena.get_mut(token).unwrap().data.variables.insert(variable_name, variable_value);
        return Ok(());
    }
    Err(())
}

fn assign_variable(arena: &mut Arena<VariableScope>, token: Token, variable_name: String, mut variable_value: String) -> Result<(), ()> {
    if arena.get(token).unwrap().data.variables.contains_key(&*variable_name) {
        arena.get_mut(token).unwrap().data.variables.insert(variable_name, variable_value);
        return Ok(());
    } else {
        for parent in arena.get(token).unwrap().ancestors_tokens(arena).next() {
            match arena.get_mut(parent) {
                None => { continue; }
                Some(parent_variables) => {
                    if parent_variables.data.variables.contains_key(&*variable_name) {
                        parent_variables.data.variables.insert(variable_name.clone(), variable_value.clone());
                        return Ok(());
                    }
                }
            }
        }
    }
    Err(())
}

#[cfg(test)]
mod tests {
    use atree::Arena;
    use crate::variable_scope::{VariableScope, is_variable, find_variable, assign_variable, create_variable};
    use std::collections::HashMap;

    #[test]
    fn has_variable_in_local_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert("myVar".parse().unwrap(), "'1'".parse().unwrap());
        let (mut arena, root_token) = Arena::with_data(top_scope);

        assert_eq!(is_variable(&arena, root_token, &String::from("myVar")), true);
    }

    #[test]
    fn has_no_variable_in_local_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        let (mut arena, root_token) = Arena::with_data(top_scope);

        assert_eq!(is_variable(&arena, root_token, &String::from("myVar")), false);
    }

    #[test]
    fn has_variable_in_parent_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert("myVar".parse().unwrap(), "'1'".parse().unwrap());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let current_variable_scope = VariableScope { variables: HashMap::new() };
        let current_variable_scope_token = root_token.append(&mut arena, current_variable_scope);
        assert_eq!(is_variable(&arena, current_variable_scope_token, &String::from("myVar")), true);
    }

    #[test]
    fn has_no_variable_in_parent_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let current_variable_scope = VariableScope { variables: HashMap::new() };
        let current_variable_scope_token = root_token.append(&mut arena, current_variable_scope);
        assert_eq!(is_variable(&arena, current_variable_scope_token, &String::from("myVar")), false);
    }

    #[test]
    fn find_variable_in_local_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert("myVar".parse().unwrap(), "'1'".parse().unwrap());
        let (mut arena, root_token) = Arena::with_data(top_scope);

        assert_eq!(find_variable(&arena, root_token, &String::from("myVar")), Some(String::from("'1'")));
    }

    #[test]
    fn fail_to_find_variable_in_local_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        let (mut arena, root_token) = Arena::with_data(top_scope);

        assert_eq!(find_variable(&arena, root_token, &String::from("myVar")), None);
    }

    #[test]
    fn find_variable_in_parent_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert("myVar".parse().unwrap(), "'1'".parse().unwrap());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let current_variable_scope = VariableScope { variables: HashMap::new() };
        let current_variable_scope_token = root_token.append(&mut arena, current_variable_scope);
        assert_eq!(find_variable(&arena, current_variable_scope_token, &String::from("myVar")), Some(String::from("'1'")));
    }

    #[test]
    fn fail_to_find_variable_in_parent_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let current_variable_scope = VariableScope { variables: HashMap::new() };
        let current_variable_scope_token = root_token.append(&mut arena, current_variable_scope);
        assert_eq!(find_variable(&arena, current_variable_scope_token, &String::from("myVar")), None);
    }

    #[test]
    fn assign_variable_not_in_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        let expected = Err(());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let result = assign_variable(&mut arena, root_token, String::from("myVar"), String::from("'1'"));
        assert_eq!(result, expected);
    }

    #[test]
    fn assign_variable_in_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert(String::from("myVar"), String::from("'2'"));
        let expected = Ok(());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let result = assign_variable(&mut arena, root_token, String::from("myVar"), String::from("'1'"));
        assert_eq!(result, expected);
        assert_eq!(arena.get(root_token).unwrap().data.variables.get("myVar").unwrap().clone(), String::from("'1'"));
    }

    #[test]
    fn assign_variable_in_parent_scope() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert(String::from("myVar"), String::from("'2'"));
        let expected = Ok(());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let current_variable_scope = VariableScope { variables: HashMap::new() };
        let current_variable_scope_token = root_token.append(&mut arena, current_variable_scope);
        let result = assign_variable(&mut arena, current_variable_scope_token, String::from("myVar"), String::from("'1'"));
        assert_eq!(result, expected);
        assert_eq!(arena.get(root_token).unwrap().data.variables.get("myVar").unwrap().clone(), String::from("'1'"));
    }

    #[test]
    fn successfully_create_variable() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert(String::from("myVar"), String::from("'2'"));
        let expected = Ok(());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let result = create_variable(&mut arena, root_token, String::from("myVar2"), String::from("'1'"));
        assert_eq!(result, expected);
        assert_eq!(arena.get(root_token).unwrap().data.variables.get("myVar2").unwrap().clone(), String::from("'1'"));
    }

    #[test]
    fn fail_to_create_variable() {
        let mut top_scope = VariableScope { variables: HashMap::new() };
        top_scope.variables.insert(String::from("myVar"), String::from("'2'"));
        let expected = Err(());
        let (mut arena, root_token) = Arena::with_data(top_scope);
        let result = create_variable(&mut arena, root_token, String::from("myVar"), String::from("'1'"));
        assert_eq!(result, expected);
    }
}
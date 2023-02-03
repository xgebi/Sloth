use pgs_nodes::node::Node;

pub fn add(left: usize, right: usize) -> usize {
    let a = Node { name: String::new() };
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}

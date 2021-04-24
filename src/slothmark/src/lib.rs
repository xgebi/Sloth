struct ListInfo {
    indent: u8,
    level: u16,
    list_type: str,
    parent: ListInfo
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

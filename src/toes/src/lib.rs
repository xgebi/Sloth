#![feature(in_band_lifetimes)]

mod toe_parser;
mod nodes;
mod xml_parsing_info;

mod toes {
    pub fn make_sausage() {
        println!("sausage!");
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

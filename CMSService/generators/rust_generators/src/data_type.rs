use std::collections::HashMap;
use std::fmt::{format, Display, Formatter};
use pyo3::pyclass;
use unicode_segmentation::UnicodeSegmentation;

#[derive(Debug, Clone, PartialEq)]
pub enum DataType {
    Nil,
    Boolean(bool),
    String(String),
    Int(usize),
    Float(f64),
    Array(Vec<DataType>),
    HashMap(HashMap<String, DataType>)
}

impl Display for DataType {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            DataType::Nil => { write!(f, "") }
            DataType::Boolean(b) => {write!(f, "{}", if b.clone() { "true" } else { "false" })}
            DataType::String(s) => { write!(f, "{}", s) }
            DataType::Int(i) => { write!(f, "{}", i) }
            DataType::Float(fl) => { write!(f, "{}", fl) }
            DataType::Array(ar) => {
                let mut res = "[".to_string();
                for item in ar {
                    res.push_str(format!("{}", item.to_string()).as_str());
                }
                res.push_str("]");
                write!(f, "{}", res)
            }
            DataType::HashMap(_) => { write!(f, "{}", todo!()) }
        }
    }
}

impl From<String> for DataType {
    fn from(value: String) -> Self {
        let value_arr = value.graphemes(true).collect::<Vec<&str>>();
        if value_arr.len() == 0{
            return DataType::Nil;
        }
        // This decision might have to be revised
        if value_arr[0] == "\"" || value_arr[0] == "'" || value_arr[0] == "`" {
            let mut temp_value = value.clone();
            temp_value.remove(0);
            temp_value.remove(temp_value.len() - 1);
            return DataType::String(temp_value);
        }
        if value.trim() == "true" || value.trim() == "false" {
            return DataType::Boolean(value == "true");
        }
        let parsed_float = value.parse::<f64>();
        if parsed_float.is_ok() && value.contains(".") {
            return DataType::Float(parsed_float.unwrap());
        } else if parsed_float.is_ok() && !value.contains(".") {
            return DataType::Int(value.parse::<usize>().unwrap());
        }
        if value_arr[0] == "[" && value_arr[value_arr.len() - 1] == "]" {
            let mut res_string = Vec::new();
            let mut i = 1;
            let mut current_value = String::new();
            let mut is_space_in_quote = false;
            let mut quotation_mark: String = String::new();
            while i < value_arr.len() - 1 {
                if value_arr[i] != "," {
                    current_value.push_str(value_arr[i]);
                    if is_space_in_quote {
                        if value_arr[i] == quotation_mark {
                            is_space_in_quote = false;
                            quotation_mark = String::new();
                        }
                    } else if value_arr[i] == "'" ||
                        value_arr[i] == "\"" ||
                        value_arr[i] == "`" {
                        is_space_in_quote = true;
                        quotation_mark = value_arr[i].to_string();
                    }
                    if i + 2 == value_arr.len() {
                        res_string.push(current_value.clone());
                        current_value = String::new();
                    }
                } else {
                    if is_space_in_quote {
                        current_value.push_str(value_arr[i]);
                    } else {
                        res_string.push(current_value.clone());
                        current_value = String::new();
                    }
                }
                i += 1;
            }
            let mut res = Vec::new();
            for item in res_string {
                res.push(DataType::from(item));
            }

            return DataType::Array(res);
        }


        DataType::Nil
    }
}

#[cfg(test)]
mod from_tests {
    use crate::data_type::DataType;

    #[test]
    fn test_from_empty_string() {
        let res = DataType::from(String::new());
        assert_eq!(res, DataType::Nil);
    }

    #[test]
    fn test_from_boolean_true_string() {
        let res = DataType::from(String::from("true"));
        assert_eq!(res, DataType::Boolean(true));
    }

    #[test]
    fn test_from_boolean_false_string() {
        let res = DataType::from(String::from("false"));
        assert_eq!(res, DataType::Boolean(false));
    }

    #[test]
    fn test_from_float_string() {
        let res = DataType::from(String::from("1.0"));
        assert_eq!(res, DataType::Float(1.0));
    }

    #[test]
    fn test_from_int_string() {
        let res = DataType::from(String::from("12"));
        assert_eq!(res, DataType::Int(12));
    }

    #[test]
    fn test_from_string() {
        let res = DataType::from(String::from("'1.0'"));
        assert_eq!(res, DataType::String(String::from("1.0")));
    }

    #[test]
    fn test_from_boolean_array_string() {
        let res = DataType::from(String::from("[true, false]"));
        println!("{:?}", res);
    }
}

impl Into<bool> for DataType {
    fn into(self) -> bool {
        match self {
            DataType::Nil => false,
            DataType::Boolean(b) => b,
            DataType::String(s) => { s.len() > 0 }
            DataType::Int(i) => { i > 0 }
            DataType::Float(fl) => { fl > 0.0 }
            DataType::Array(a) => { !a.is_empty() }
            DataType::HashMap(hm) => { !hm.is_empty() }
        }
    }
}

#[cfg(test)]
mod into_tests {
    use std::collections::HashMap;
    use crate::data_type::DataType;

    #[test]
    fn test_nil_string() {
        let res = DataType::Nil;
        assert_eq!(<DataType as Into<bool>>::into(res), false);
    }

    #[test]
    fn test_empty_string_string() {
        let res = DataType::String("".to_string());
        assert_eq!(<DataType as Into<bool>>::into(res), false);
    }

    #[test]
    fn test_non_empty_string_string() {
        let res = DataType::String(" ".to_string());
        assert_eq!(<DataType as Into<bool>>::into(res), true);
    }

    #[test]
    fn test_bool_string() {
        let res = DataType::Boolean(false);
        assert_eq!(<DataType as Into<bool>>::into(res), false);
    }

    #[test]
    fn test_zero_float_string() {
        let res = DataType::Float(0.0);
        assert_eq!(<DataType as Into<bool>>::into(res), false);
    }

    #[test]
    fn test_non_zero_float_string() {
        let res = DataType::Float(0.1);
        assert_eq!(<DataType as Into<bool>>::into(res), true);
    }

    #[test]
    fn test_zero_int_string() {
        let res = DataType::Int(0);
        assert_eq!(<DataType as Into<bool>>::into(res), false);
    }

    #[test]
    fn test_non_zero_int_string() {
        let res = DataType::Int(1);
        assert_eq!(<DataType as Into<bool>>::into(res), true);
    }

    #[test]
    fn test_empty_array_string() {
        let res = DataType::Array(vec![]);
        assert_eq!(<DataType as Into<bool>>::into(res), false);
    }

    #[test]
    fn test_non_empty_array_string() {
        let res = DataType::Array(vec![DataType::Nil]);
        assert_eq!(<DataType as Into<bool>>::into(res), true);
    }

    #[test]
    fn test_empty_hash_map_string() {
        let hm = HashMap::new();
        let res = DataType::HashMap(hm);
        assert_eq!(<DataType as Into<bool>>::into(res), false);
    }

    #[test]
    fn test_non_empty_hash_map_string() {
        let mut hm = HashMap::new();
        hm.insert("value".to_string(), DataType::Nil);
        let res = DataType::HashMap(hm);
        assert_eq!(<DataType as Into<bool>>::into(res), true);
    }
}


use std::collections::HashMap;
use std::fmt::{Display, Formatter};
use std::iter::Filter;
use std::rc::Rc;

#[derive(Clone, Debug)]
pub enum Value {
    Boolean(bool),
    Nil,
    Float(f64),
    Integer(i128),
    String(String),
    HashMap(HashMap<String, Rc<Value>>),
    Array(Vec<Rc<Value>>)
}

impl From<String> for Value {
    fn from(value: String) -> Self {
        Value::String(value.clone())
    }
}

impl From<f64> for Value {
    fn from(value: f64) -> Self {
        Value::Float(value.clone())
    }
}

impl From<i128> for Value {
    fn from(value: i128) -> Self {
        Value::Integer(value.clone())
    }
}

impl From<bool> for Value {
    fn from(value: bool) -> Self {
        Value::Boolean(value.clone())
    }
}

impl From<HashMap<String, String>> for Value {
    fn from(values: HashMap<String, String>) -> Self {
        let mut res = HashMap::new();
        for value in values {
            let key = value.0.clone();
            let val = value.1.clone();
            res.insert(key, Rc::from(Value::String(val)));
        }
        Value::HashMap(res)
    }
}

impl From<Vec<String>> for Value {
    fn from(values: Vec<String>) -> Self {
        let mut res: Vec<Rc<Value>> = vec![];
        for value in values {
            res.push(Rc::from(Value::String(value.clone())));
        }
        Value::Array(res)
    }
}

impl From<Vec<HashMap<String, String>>> for Value {
    fn from(values: Vec<HashMap<String, String>>) -> Self {
        let mut res = vec![];
        for value in values {
            let val = value.clone();
            res.push(Rc::from(Value::from(value.clone())));
        }
        Value::Array(res)
    }
}

#[cfg(test)]
mod value_tests {
    use crate::value::Value;

    #[test]
    fn is_string_created() {
        let val = Value::from(String::from("ABC"));
        match val {
            Value::String(_) => {
                assert_eq!(val.to_string(), "ABC")
            }
            _ => {
                assert_eq!(true, false)
            }
        }
    }

    #[test]
    fn is_integer_created() {
        let val = Value::from(1);
        match val {
            Value::Integer(_) => {
                let v = Value::Integer(1);
                assert_eq!(val == v, true)
            }
            _ => {
                assert_eq!(true, false)
            }
        }
    }

    #[test]
    fn is_float_created() {
        let val = Value::from(1.0);
        match val {
            Value::Float(_) => {
                let v = Value::Float(1.0);
                assert_eq!(val == v, true)
            }
            _ => {
                assert_eq!(true, false)
            }
        }
    }
}

impl PartialEq for Value {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Value::Boolean(a), Value::Boolean(b)) => a == b,
            (Value::Nil, Value::Nil) => true,
            (Value::Float(a), Value::Float(b)) => a == b,
            (Value::Integer(a), Value::Integer(b)) => a == b,
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

impl Display for Value {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match (self) {
            Value::Boolean(a) => write!(f, "{}", a.clone()),
            Value::Nil => write!(f, "null"),
            Value::Float(a) => write!(f, "{}", a.clone()),
            Value::Integer(a) => write!(f, "{}", a.clone()),
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

impl Iterator for Value {
    type Item = ();

    fn next(&mut self) -> Option<Self::Item> {
        todo!()
    }

    fn count(self) -> usize
    where
        Self: Sized
    {
        todo!()
    }

    fn last(self) -> Option<Self::Item>
    where
        Self: Sized
    {
        todo!()
    }

    fn for_each<F>(self, f: F)
    where
        Self: Sized,
        F: FnMut(Self::Item)
    {
        todo!()
    }

    fn filter<P>(self, predicate: P) -> Filter<Self, P>
    where
        Self: Sized,
        P: FnMut(&Self::Item) -> bool
    {
        todo!()
    }

    fn find<P>(&mut self, predicate: P) -> Option<Self::Item>
    where
        Self: Sized,
        P: FnMut(&Self::Item) -> bool
    {
        todo!()
    }

    fn position<P>(&mut self, predicate: P) -> Option<usize>
    where
        Self: Sized,
        P: FnMut(Self::Item) -> bool
    {
        todo!()
    }

    fn rposition<P>(&mut self, predicate: P) -> Option<usize>
    where
        P: FnMut(Self::Item) -> bool,
        Self: Sized + ExactSizeIterator + DoubleEndedIterator
    {
        todo!()
    }

    fn is_sorted(self) -> bool
    where
        Self: Sized,
        Self::Item: PartialOrd
    {
        todo!()
    }
}

impl<I: Iterator> IntoIterator for Value {
    type Item = ();
    type IntoIter = ();

    fn into_iter(self) -> Self::IntoIter {
        todo!()
    }
}
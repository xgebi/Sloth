use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize, Debug, Default, PartialEq)]
pub struct Pattern {
    pub name: &'static str,
    pub value: String,
}

#[derive(Clone, Serialize, Debug)]
pub struct Patterns {
    patterns: Vec<Pattern>,
}

impl Patterns {
    pub fn new() -> Self {
        let patterns = vec![
            Pattern {
                name: "footnote",
                value: String::from(r"\[\d+\. "),
            },
            Pattern {
                name: "double_line",
                value: String::from("\n\n"),
            },
            Pattern {
                name: "double_line_win",
                value: String::from("\r\n\r\n"),
            },
            Pattern {
                name: "not_paragraph",
                value: String::from(r"[-\d#]"),
            },
            Pattern {
                name: "ordered_list",
                value: String::from(r"\d+\. "),
            },
            Pattern {
                name: "new_line_ordered_list",
                value: String::from(r"\n\d+\. "),
            },
            Pattern {
                name: "unordered_list",
                value: String::from("- "),
            },
            Pattern {
                name: "unordered_list_alt",
                value: String::from("* "),
            },
            Pattern {
                name: "new_line_unordered_list",
                value: String::from(r"\n- "),
            },
            Pattern {
                name: "image",
                value: String::from("!["),
            },
            Pattern {
                name: "codeblock",
                value: String::from("```"),
            },
        ];

        Self { patterns }
    }

    pub fn locate(&self, name: &str) -> Option<Pattern> {
        self.patterns.iter().find(|p| p.name == name).cloned()
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_item() {
        let pat = Patterns::new();
        assert_ne!(pat.locate("codeblock"), None);
    }

    #[test]
    fn finds_nothing() {
        let pat = Patterns::new();
        assert_eq!(pat.locate("non-sense"), None);
    }
}
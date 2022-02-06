use std::ops::Add;
use unicode_segmentation::UnicodeSegmentation;
use crate::common::HtmlNode::HtmlNode;

enum ListType {
    Numbered,
    Bulleted
}

struct ListInfo<'a> {
    indent: u8,
    level: i16,
    list_type: ListType,
    parent: Option<&'a ListInfo<'a>>
}

impl ListInfo<'a> {
    fn new(indent: Option<u8>, level: u16, list_type: ListType, parent: Option<&'a ListInfo<'a>>) -> Self {
        let list_level: i16 = if parent.is_none() { 0 } else { parent.unwrap().level + 1 };
        Self {
            indent: indent.unwrap_or(2),
            level: list_level,
            list_type,
            parent
        }
    }
}

struct Footnote {
    index: u32,
    footnote: String
}

struct Footnotes {
    footnotes: Vec<Footnote>
}

impl Footnotes {
    fn combine_footnotes(mut self, text: String) -> String {
        if self.footnotes.is_empty() {
            return text
        }
        self.footnotes.sort_by_key(|f| { f.index });
        let mut result = format!("{}<h2>Footnotes</h2><ol>", text);
        for footnote in self.footnotes {
            result.add(footnote.footnote.as_str());
        }
        result
    }
}

pub(crate) struct MarkdownParser {
    graphemes: Vec<String>
}

impl MarkdownParser {
    pub(crate) fn new(md_text: String) -> Self {
        let gs = md_text.graphemes(true).collect::<Vec<&str>>().iter().map(|x| { x.to_string()}).collect::<Vec<String>>();
        MarkdownParser {
            graphemes: gs
        }
    }

    pub(crate) fn get_html_code(self) -> String {
        "".into()
    }

    fn create_node_tree(self) -> HtmlNode {
        let root_node = HtmlNode {

        };
        let current_node: &HtmlNode = &root_node;
        for (index, grapheme) in self.graphemes.iter().enumerate() {

        }
        root_node
    }
}
use unicode_segmentation::UnicodeSegmentation;
use crate::common::HtmlNode::HtmlNode;

pub(crate) struct MarkdownParser<'a> {
    graphemes: Vec<&'a str>
}

impl MarkdownParser {
    pub(crate) fn new(md_text: String) -> Self {
        MarkdownParser {
            graphemes: md_text.graphemes(true).collect::<Vec<&str>>()
        }
    }

    pub(crate) fn get_html_code(self) -> String {
        "".into()
    }

    ///
    ///
    fn create_node_tree(self) -> HtmlNode {
        let root_node = HtmlNode {

        };
        let current_node: &HtmlNode = &root_node;
        for (index, grapheme) in self.graphemes.iter().enumerate() {

        }
        root_node
    }
}
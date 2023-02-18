use std::thread::current;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use regex::Regex;

static FOOTNOTE_PATTERN: &str = r"\[\d+\. ";
static DOUBLE_NEW_LINE: &str = "\n\n";
static DOUBLE_NEW_LINE_WIN: &str = "\r\n\r\n";
static NOT_PARAGRAPH_PATTERN: &str = r"[-\d#]";
static ORDERED_LIST_PATTERN: &str = r"\d+\. ";
static NEW_LINE_ORDERED_LIST_PATTERN: &str = r"\n\d+\. ";
static UNORDERED_LIST_PATTERN: &str = r"- ";
static UNORDERED_LIST_PATTERN_ALT: &str = r"* ";
static NEW_LINE_UNORDERED_LIST_PATTERN: &str = r"\n- ";
static IMAGE_PATTERN: &str = r"![";
static CODEBLOCK_PATTERN: &str = r"```";

pub fn render_markup(md: String) -> String {
    // 1. parse markdown to nodes
    let res_node = parse_slothmark(md);
    // 2. call node::to_string() to create result
    res_node.to_string()
}

fn parse_slothmark(sm: String) -> (Node, Node) {
    let g = sm.graphemes(true).collect::<Vec<&str>>();
    // 1. loop through sm
    let mut root_node = Node::create_node(None, Some(NodeType::Root));
    let mut footnotes = Node::create_node(Some(String::from("ul")), Some(NodeType::Node));
    let mut current_node = &root_node;
    let mut i: usize = 0;
    while i < g.len() {
        // process paragraph
        let p_pattern = Regex::new(NOT_PARAGRAPH_PATTERN).unwrap();
        let ordered_list_regex = Regex::new(ORDERED_LIST_PATTERN).unwrap();
        if (i == 0 || g[i - 1] == "\n") && !p_pattern.is_match(g[i]) {
            let mut p = Node::create_node(Some(String::from("p")), None);
            let t = process_content(g[i..g.len()].to_vec());
            i += t.2;
            p.children.extend(t[0]);
            footnotes.children.extend(t.1);
            current_node = &p;

            root_node.children.push(p);
        } else if g[i] == "#" {
            // case for h*
            process_headline(g[i..g.len()].to_vec());
        } else if g[i..i+2].join("") == UNORDERED_LIST_PATTERN &&
            ((i > 0 && g[i-1] == "\n") || i == 0) {
            // case for unordered list
            process_unordered_list(g[i..g.len()].to_vec());
        } else if ((i > 0 && g[i-1] == "\n") || i == 0) &&
            ordered_list_regex.is_match_at(g[i..g.len()].join("").as_str(), 0) {
            // Add if case for ordered list
            process_ordered_list(g[i..g.len()].to_vec());
        } else if g[i..i+2].join("") == IMAGE_PATTERN{
            // Add if case for image
            process_image(g[i..g.len()].to_vec());
        } else if g[i..i+3].join("") == CODEBLOCK_PATTERN {
            // Add if case for code block
            process_code_block(g[i..g.len()].to_vec());
        }
    }

    (root_node, footnotes)
}

fn process_content(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, usize) {
    let mut i: usize = 0;
    let mut current_node = Node::create_text_node(String::new());
    let mut nodes = Vec::new();
    let mut footnotes = Vec::new();
    let footnote_pattern = Regex::new(FOOTNOTE_PATTERN).unwrap();
    while i < c.len() {
        // Add quit cases for headline, code block and lists
        if (i+1 < c.len() && c[i..i+2].join("") == DOUBLE_NEW_LINE) ||
            (i+3 < c.len() && c[i..i+4].join("") == DOUBLE_NEW_LINE_WIN) {
            nodes.push(current_node);
            return (nodes, footnotes, i + 1);
        } else if c[i] != "\n" || c[i] != "\r" {
            current_node.content = format!("{}{}", current_node.content, c[i]);
        } else if c[i..i+3].join("**") == "" {
            // clause for bold
            process_bold(c[i..c.len()].into_vec())
        } else if c[i] == "*" {
            // clause for italic
            process_italic(c[i..c.len()].into_vec())
        } else if footnote_pattern.is_match(c[i..i+2].join("").as_str()) {
            // clause for footnotes
            let end_index = c[i+2..c.len()].join("").find("]");
        } else if c[i] == "[" {
            // clause for links
            let middle_index = c[i+2..c.len()].join("").find("](");
            let end_index = c[i+2..c.len()].join("").find(")");
        } else if c[i..i+2].join("") == IMAGE_PATTERN {
            // clause for images
            let end_index = c[i+2..c.len()].join("").find("]");
        } else if c[i] == "`" {
            // clause for inline code
            let end_index = c[i+2..c.len()].join("").find("```\n");
        } else {
            current_node.content = format!("{}{}", current_node.content, " ");
        }
        i += 1;
    }
    (nodes, footnotes, c.len())
}

fn process_headline(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

fn process_image(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

fn process_link(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

fn process_inline_code(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

fn process_code_block(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

fn process_footnote(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

// Not tested yet
fn process_bold(c: Vec<&str>) -> (Option<Node>, Vec<Node>, i) {
    let end_index = c[i+2..c.len()].join("").find("**");
    match end_index {
        Some(i) => {
            let mut bold = Node::create_node(Some(String::from("b")), Some(NodeType::Node));
            let r = process_content(c[i+2..end_index].into_vec());
            bold.children.extend(r.0);
            (Some(bold), r.1, end_index + 1)
        },
        None => {
            (None, vec![], 0)
        }
    }
}

// Not tested yet
fn process_italic(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    let end_index = c[i+2..c.len()].join("").find("*");
    match end_index {
        Some(i) => {
            let mut italic = Node::create_node(Some(String::from("i")), Some(NodeType::Node));
            let r = process_content(c[i+2..end_index].into_vec());
            italic.children.extend(r.0);
            (Some(italic), r.1, end_index + 1)
        },
        None => {
            (None, vec![], 0)
        }
    }
    (vec![], vec![], 0)
}

fn process_ordered_list(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

fn process_unordered_list(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

fn process_list_item(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, i) {
    (vec![], vec![], 0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn renders_empty() {
        let result = render_markup(String::from(""));
        assert_eq!(result, String::from(""));
    }

    #[test]
    fn renders_paragraph() {
        let result = render_markup(String::from("Abc"));
        assert_eq!(result, String::from("<p>Abc</p>"));
    }

    #[test]
    fn process_empty_content() {
        let result = process_content("".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "");
    }

    #[test]
    fn process_paragraph_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_link_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_italic_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_bold_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_bold_italic_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_footnote_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_image_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_inline_code_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.content, "Abc");
    }

    // #[test]
    // fn renders_ordered_list() {
    //     let result = render_markup(String::from("1. abc\n2. def"));
    //     assert_eq!(result, String::from("<ol><li>abc</li><li>def</li></ol>"));
    // }
    //
    // #[test]
    // fn renders_unordered() {
    //     let result = render_markup(String::from("- abc\n- def"));
    //     assert_eq!(result, String::from("<ul><li>abc</li><li>def</li></ul>"));
    // }
    //
    // #[test]
    // fn renders_h1() {
    //     let result = render_markup(String::from("# ABC"));
    //     assert_eq!(result, String::from("<h1>ABC</h1>"));
    // }
    //
    // #[test]
    // fn renders_h2() {
    //     let result = render_markup(String::from("## ABC"));
    //     assert_eq!(result, String::from("<h2>ABC</h2>"));
    // }
    // #[test]
    // fn renders_h3() {
    //     let result = render_markup(String::from("### ABC"));
    //     assert_eq!(result, String::from("<h3>ABC</h3>"));
    // }
    // #[test]
    // fn renders_h4() {
    //     let result = render_markup(String::from("#### ABC"));
    //     assert_eq!(result, String::from("<h4>ABC</h4>"));
    // }
    // #[test]
    // fn renders_h5() {
    //     let result = render_markup(String::from("##### ABC"));
    //     assert_eq!(result, String::from("<h5>ABC</h5>"));
    // }
    // #[test]
    // fn renders_h6() {
    //     let result = render_markup(String::from("###### ABC"));
    //     assert_eq!(result, String::from("<h6>ABC</h6>"));
    // }
}

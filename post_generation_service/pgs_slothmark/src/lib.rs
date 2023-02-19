
use std::thread::current;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use pgs_common::patterns::Patterns;
use regex::Regex;

enum ListType {
    Ordered,
    Unordered
}

pub fn render_markup(md: String) -> String {
    // 1. parse markdown to nodes
    let res_node = parse_slothmark(md);
    // 2. call node::to_string() to create result
    format!("{}{}", res_node.0.to_string(), res_node.1.to_string())
}

fn parse_slothmark(sm: String) -> (Node, Node) {
    let patterns = Patterns::new();
    let processed_new_lines = sm.replace(
        patterns.locate("double_line_win").unwrap().value.as_str(),
        patterns.locate("double_line").unwrap().value.as_str()
    );
    let grapheme_vector = processed_new_lines.graphemes(true).collect::<Vec<&str>>();
    // 1. loop through sm
    let mut root_node = Node::create_node(None, Some(NodeType::Root));
    let mut footnotes = Node::create_node(Some(String::from("ul")), Some(NodeType::Node));
    let mut current_node = &root_node;
    let mut i: usize = 0;
    while i < grapheme_vector.len() {
        // process paragraph
        let p_pattern = Regex::new(patterns.locate("not_paragraph").unwrap().value.as_str()).unwrap();
        let ordered_list_regex = Regex::new(patterns.locate("ordered_list").unwrap().value.as_str()).unwrap();
        if (i == 0 || grapheme_vector[i - 1] == "\n") && !p_pattern.is_match(grapheme_vector[i]) {
            let mut p = Node::create_node(Some(String::from("p")), None);
            let t = process_content(grapheme_vector[i..grapheme_vector.len()].to_vec(), true);
            i += t.2;
            p.children.extend(t.0);
            footnotes.children.extend(t.1);
            current_node = &p;

            root_node.children.push(p);
        } else if grapheme_vector[i] == "#" {
            // case for h*
            let mut p = Node::create_node(Some(String::from("p")), None);
            let t = process_headline(grapheme_vector[i..grapheme_vector.len()].to_vec());
            i += t.2;
            p.children.extend(t.0);
            footnotes.children.extend(t.1);
            current_node = &p;

            root_node.children.push(p);
        } else if (grapheme_vector[i..i+2].join("") == patterns.locate("unordered_list").unwrap().value ||
            grapheme_vector[i..i+2].join("") == patterns.locate("unordered_list_alt").unwrap().value) &&
            ((i > 0 && grapheme_vector[i-1] == "\n") || i == 0) {
            // case for unordered list
            process_list_items(
                grapheme_vector[i..grapheme_vector.len()].to_vec(),
                String::new(),
                String::from(grapheme_vector[i])
            );
            let mut p = Node::create_node(Some(String::from("p")), None);
            let t = process_headline(grapheme_vector[i..grapheme_vector.len()].to_vec());
            i += t.2;
            p.children.extend(t.0);
            footnotes.children.extend(t.1);
            current_node = &p;

            root_node.children.push(p);
        } else if ((i > 0 && grapheme_vector[i-1] == "\n") || i == 0) &&
            ordered_list_regex.is_match_at(grapheme_vector[i..grapheme_vector.len()].join("").as_str(), 0) {
            // Add if case for ordered list
            let mut p = Node::create_node(Some(String::from("ol")), None);
            let t = process_list_items(grapheme_vector[i..grapheme_vector.len()].to_vec(), String::new(), String::from(r"\d"));
            i += t.2;
            p.children.extend(t.0);
            footnotes.children.extend(t.1);
            current_node = &p;

            root_node.children.push(p);
        } else if grapheme_vector[i..i+2].join("") == patterns.locate("image").unwrap().value {
            // Add if case for image
            let mut p = Node::create_node(Some(String::from("img")), None);
            let t = process_image(grapheme_vector[i..grapheme_vector.len()].to_vec());
            i += t.1;
            if let Some(image) = t.0 {
                root_node.children.push(image);
            }
        } else if grapheme_vector[i..i+3].join("") == patterns.locate("codeblock").unwrap().value {
            // Add if case for code block
            process_code_block(grapheme_vector[i..grapheme_vector.len()].to_vec());
        }
    }

    (root_node, footnotes)
}

fn process_content(c: Vec<&str>, inline: bool) -> (Vec<Node>, Vec<Node>, usize) {
    let patterns = Patterns::new();
    let mut i: usize = 0;
    let mut current_node = Node::create_text_node(String::new());
    let mut nodes = Vec::new();
    let mut footnotes = Vec::new();
    let footnote_pattern = Regex::new(patterns.locate("footnote").unwrap().value.as_str()).unwrap();
    while i < c.len() {
        // Add quit cases for headline, code block and lists
        if i+1 < c.len() && c[i..i+3].join("") == patterns.locate("double_line").unwrap().value {
            nodes.push(current_node);
            return (nodes, footnotes, i + 1);
        } else if c[i] != "\n" || c[i] != "\r" {
            current_node.content = format!("{}{}", current_node.content, c[i]);
        } else if c[i..i+3].join("**") == "" {
            // clause for bold
            let r = process_bold(c[i..c.len()].to_vec());
            current_node.children.push(r.0.unwrap());
            footnotes.extend(r.1);
            i += r.2;
        } else if c[i] == "*" {
            // clause for italic
            process_italic(c[i..c.len()].to_vec());
        } else if footnote_pattern.is_match(c[i..i+2].join("").as_str()) {
            // clause for footnotes
            let end_index = c[i+2..c.len()].join("").find("]");
        } else if c[i] == "[" {
            // clause for links
            let middle_index = c[i+2..c.len()].join("").find("](");
            let end_index = c[i+2..c.len()].join("").find(")");
        } else if c[i..i+2].join("") == patterns.locate("image").unwrap().value {
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

fn process_headline(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, usize) {
    (vec![], vec![], 0)
}

fn process_image(c: Vec<&str>) -> (Option<Node>, usize) {
    (None, 0)
}

fn process_link(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, usize) {
    (vec![], vec![], 0)
}

fn process_inline_code(c: Vec<&str>) -> (Option<Node>, usize) {
    (None, 0)
}

fn process_code_block(c: Vec<&str>) -> (Option<Node>, usize) {
    (None, 0)
}

fn process_footnote(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, usize) {
    (vec![], vec![], 0)
}

// Not tested yet
fn process_bold(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let end_index = c[2..c.len()].join("").find("**");
    match end_index {
        Some(i) => {
            let mut bold = Node::create_node(Some(String::from("b")), Some(NodeType::Node));
            let r = process_content(c[2..i].to_vec(), true);
            bold.children.extend(r.0);
            (Some(bold), r.1, i + 1)
        },
        None => {
            (None, vec![], 0)
        }
    }
}

// Not tested yet
fn process_italic(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let end_index = c[2..c.len()].join("").find("*");
    match end_index {
        Some(i) => {
            let mut italic = Node::create_node(Some(String::from("i")), Some(NodeType::Node));
            let r = process_content(c[2..i].to_vec(), true);
            italic.children.extend(r.0);
            (Some(italic), r.1, i + 1)
        },
        None => {
            (None, vec![], 0)
        }
    }
}

fn process_list_items(c: Vec<&str>, offset: String, list_type: String) -> (Vec<Node>, Vec<Node>, usize) {
    let mut i = 0;
    while i < c.len() {

    }
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
        let result = process_content("".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.content, "");
    }

    #[test]
    fn process_paragraph_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_link_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_italic_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_bold_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_bold_italic_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_footnote_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_image_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.content, "Abc");
    }

    #[test]
    fn process_inline_code_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
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

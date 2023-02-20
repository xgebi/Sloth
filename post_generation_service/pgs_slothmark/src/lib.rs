
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
    if res_node.1.children.len() > 0 {
        return format!("{}{}", res_node.0.to_string(), res_node.1.to_string());
    }
    format!("{}", res_node.0.to_string())
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
        } else if i+1 < grapheme_vector.len() && grapheme_vector[i..i+2].join("") == patterns.locate("image").unwrap().value {
            // Add if case for image
            let mut p = Node::create_node(Some(String::from("img")), None);
            let t = process_image(grapheme_vector[i..grapheme_vector.len()].to_vec());
            i += t.1;
            if let Some(image) = t.0 {
                root_node.children.push(image);
            }
        } else if i + 3 < grapheme_vector.len() && grapheme_vector[i..i+3].join("") == patterns.locate("codeblock").unwrap().value {
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
    let j = c.len();
    while i < j {
        let l = c[i];
        // Add quit cases for headline, code block and lists
        if i+1 < c.len() && c[i..i+2].join("") == patterns.locate("double_line").unwrap().value {
            nodes.push(current_node);
            return (nodes, footnotes, i + 2);
        } else if i+2 < c.len() && c[i..i+2].join("") == "**" {
            if current_node.content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_text_node(String::new());
            }
            // clause for bold
            let r = process_bold(c[i..c.len()].to_vec());
            if let Some(strong) = r.0 {
                nodes.push(strong);
                footnotes.extend(r.1);
                i += r.2;
            } else {
                i += 1; // just to be safe
            }
        } else if c[i] == "*" {
            if current_node.content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_text_node(String::new());
            }
            current_node = Node::create_text_node(String::new());
            // clause for italic
            let r = process_italic(c[i..c.len()].to_vec());
            // current_node.children.push(r.0.unwrap());
            if let Some(em) = r.0 {
                nodes.push(em);
                footnotes.extend(r.1);
                i += r.2;
            } else {
                i += 1; // just to be safe
            }
        } else if i+1 < c.len() && footnote_pattern.is_match(c[i..i+2].join("").as_str()) {
            // clause for footnotes
            let end_index = c[i+2..c.len()].join("").find("]");
            i += 1;
        } else if c[i] == "[" {
            // clause for links
            let r = process_link(c[i..c.len()].to_vec());
            if let Some(link) = r.0 {
                nodes.push(link);
                footnotes.extend(r.1);
                i += r.2;
            } else {
                i += 1;
            }
        } else if i+1 < c.len() && c[i..i+2].join("") == patterns.locate("image").unwrap().value {
            // clause for images
            let end_index = c[i+2..c.len()].join("").find("]");
            i += 1;
        } else if c[i] == "`" {
            // clause for inline code
            let end_index = c[i+2..c.len()].join("").find("```\n");
            i += 1;
        } else if c[i] != "\n" || c[i] != "\r" {
            current_node.content = format!("{}{}", current_node.content, c[i]);
            i += 1;
        } else {
            current_node.content = format!("{}{}", current_node.content, " ");
            i += 1;
        }
    }
    if current_node.content.len() > 0 || current_node.children.len() > 0 {
        nodes.push(current_node);
    }
    (nodes, footnotes, c.len())
}

fn process_headline(c: Vec<&str>) -> (Vec<Node>, Vec<Node>, usize) {
    (vec![], vec![], 0)
}

fn process_image(c: Vec<&str>) -> (Option<Node>, usize) {
    (None, 0)
}

fn process_link(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let middle_index = c[1..c.len()].join("").find("](").unwrap_or(usize::MAX);
    let end_index = c[1..c.len()].join("").find(")").unwrap_or(usize::MAX);
    if middle_index < c.len() && middle_index < end_index && end_index < c.len() && c.len() < usize::MAX {
        let m = c[end_index + 1];

        let mut link_node = Node::create_node(Some(String::from("a")), Some(NodeType::Node));
        link_node.attributes.insert(String::from("href"), c[middle_index + 3..end_index+1].join(""));

        let r = process_content(c[1..middle_index + 1].to_vec(), true);
        link_node.children.extend(r.0);
        return (Some(link_node), r.1, end_index + 2);
    }
    (None, vec![], 0)
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

fn process_bold(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let end_index = c[2..c.len()].join("").find("**");
    match end_index {
        Some(mut i) => {
            if c[2..c.len()].join("").find("***").is_some() && c[2..c.len()].join("").find("***").unwrap() == i {
                i += 1
            }
            let mut bold = Node::create_node(Some(String::from("strong")), Some(NodeType::Node));
            let r = process_content(c[2..i+2].to_vec(), true);
            bold.children.extend(r.0);
            (Some(bold), r.1, i + 4)
        },
        None => {
            (None, vec![], 0)
        }
    }
}

fn process_italic(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let mut end_index = c[1..c.len()].join("").find("*");
    match end_index {
        Some(mut i) => {
            while i + 2 < c.len() && c[i + 2] == "*" {
                let bold_end_temp = c[i + 2..c.len()].join("").find("**");
                if let Some(bold_end) = bold_end_temp {
                    i += bold_end + 2;
                } else {
                    i += 1
                }
            }
            let mut italic = Node::create_node(Some(String::from("em")), Some(NodeType::Node));
            let r = process_content(c[1..i+1].to_vec(), true);
            italic.children.extend(r.0);
            (Some(italic), r.1, i + 2)
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
    fn renders_two_paragraphs() {
        let result = render_markup(String::from("Abc\n\ndef"));
        println!("{:?}", result);
        assert_eq!(result, String::from("<p>Abc</p><p>def</p>"));
    }

    #[test]
    fn process_empty_content() {
        let result = process_content("".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.0.len(), 0);
    }

    #[test]
    fn process_paragraph_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.0.len(), 1);
    }

    #[test]
    fn process_link_content() {
        let result = process_content("[Abc](def)".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.get("href").unwrap(), "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].content, "Abc");
    }

    #[test]
    fn process_bold_link_content() {
        let result = process_content("[**Abc**](def)".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.get("href").unwrap(), "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
    }

    #[test]
    fn process_italic_link_content() {
        let result = process_content("[*Abc*](def)".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.get("href").unwrap(), "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "em");
    }

    #[test]
    fn process_bold_italic_link_content() {
        let result = process_content("[***Abc***](def)".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.get("href").unwrap(), "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
    }

    // #[test]
    // fn process_image_link_content() {
    //     let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
    //     assert_eq!(result.0.content, "Abc");
    // }

    #[test]
    fn process_italic_content() {
        let result = process_content("*Abc*".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "em");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].content, "Abc");
    }

    #[test]
    fn process_bold_content() {
        let result = process_content("**Abc**".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "strong");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].content, "Abc");
    }

    #[test]
    fn process_bold_italic_content_a() {
        let result = process_content("***Abc* def**".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "strong");
        assert_eq!(result.0[0].children.len(), 2);
        assert_eq!(result.0[0].children[1].content, " def");
    }

    #[test]
    fn process_bold_italic_content_b() {
        let result = process_content("*Abc **def***".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        // assert_eq!(result.0[0].name, "strong");
        // assert_eq!(result.0[0].children.len(), 2);
        // assert_eq!(result.0[0].children[1].content, " def");
    }

    #[test]
    fn process_bold_italic_content_c() {
        let result = process_content("mno *Abc **def*** jkl".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 3);
        // assert_eq!(result.0[0].name, "strong");
        // assert_eq!(result.0[0].children.len(), 2);
        // assert_eq!(result.0[0].children[1].content, " def");
    }

    #[test]
    fn process_bold_italic_content_d() {
        let result = process_content("*Abc **def*** jkl".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 2);
        // assert_eq!(result.0[0].name, "strong");
        // assert_eq!(result.0[0].children.len(), 2);
        // assert_eq!(result.0[0].children[1].content, " def");
    }

    #[test]
    fn process_bold_italic_content_e() {
        let result = process_content("mno *Abc **def***".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 2);
        // assert_eq!(result.0[0].name, "strong");
        // assert_eq!(result.0[0].children.len(), 2);
        // assert_eq!(result.0[0].children[1].content, " def");
    }

    // #[test]
    // fn process_bold_italic_content() {
    //     let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
    //     assert_eq!(result.0.content, "Abc");
    // }
    //
    // #[test]
    // fn process_footnote_content() {
    //     let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), false);
    //     assert_eq!(result.0.content, "Abc");
    // }
    //
    // #[test]
    // fn process_image_content() {
    //     let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), false);
    //     assert_eq!(result.0.content, "Abc");
    // }
    //
    // #[test]
    // fn process_inline_code_content() {
    //     let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
    //     assert_eq!(result.0.content, "Abc");
    // }

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

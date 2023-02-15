use std::thread::current;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use regex::Regex;

pub fn render_markup(md: String) -> String {
    // 1. parse markdown to nodes
    let res_node = parse_slothmark(md);
    // 2. call node::to_string() to create result
    res_node.to_string()
}

fn parse_slothmark(sm: String) -> Node {
    let g = sm.graphemes(true).collect::<Vec<&str>>();
    // 1. loop through sm
    let mut root_node = Node::create_node(None, Some(NodeType::Root));
    let mut current_node = &root_node;
    let mut i: usize = 0;
    while i < g.len() {
        // process paragraph
        let p_pattern = Regex::new(r"-\d").unwrap();
        if i == 0 && !p_pattern.is_match(g[i]) {
            let mut p = Node::create_node(Some(String::from("p")), None);
            let t = process_content(g[i..g.len()].to_vec());
            i += t.content.len();
            p.children.push(t);
            current_node = &p;

            root_node.children.push(p);
        }
    }

    root_node
}

fn process_content(c: Vec<&str>) -> Node {
    let mut i: usize = 0;
    let mut current_node = Node::create_text_node(String::new());
    while i < c.len() {
        if (i+1 < c.len() && c[i..i+2].join("") == "\n\n") ||
            (i+3 < c.len() && c[i..i+4].join("") == "\n\r\n\r") {
            return current_node;
        } else if c[i] != "\n" || c[i] != "\r"{
            current_node.content = format!("{}{}", current_node.content, c[i]);
        } else {
            current_node.content = format!("{}{}", current_node.content, " ");
        }
        i += 1;
    }
    current_node
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

    // #[test]
    // fn renders_ordered_list() {
    //     let result = render_markup(String::from(""));
    //     assert_eq!(result, String::from(""));
    // }
    //
    // #[test]
    // fn renders_unordered() {
    //     let result = render_markup(String::from(""));
    //     assert_eq!(result, String::from(""));
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


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
        if grapheme_vector[i] == "#" {
            // case for h*
            let t = process_headline(grapheme_vector[i..grapheme_vector.len()].to_vec());
            i += t.2;
            footnotes.children.extend(t.1);
            if let Some(headline) = t.0 {
                root_node.children.push(headline);
            }
        } else if (grapheme_vector[i..i+2].join("") == patterns.locate("unordered_list").unwrap().value ||
            grapheme_vector[i..i+2].join("") == patterns.locate("unordered_list_alt").unwrap().value) && // there's a bug here for ordered lists
            ((i > 0 && grapheme_vector[i-1] == "\n") || i == 0) {
            let mut list = Node::create_node(Some("ul".to_string()), Some(NodeType::Node));

            // case for unordered list
            let t = process_list_items(
                grapheme_vector[i..grapheme_vector.len()].to_vec(),
                String::from(grapheme_vector[i])
            );
            i += t.2;
            list.children.extend(t.0);
            root_node.children.push(list);
            footnotes.children.extend(t.1);
        } else if ((i > 0 && grapheme_vector[i-1] == "\n") || i == 0) &&
            ordered_list_regex.is_match_at(grapheme_vector[i..grapheme_vector.len()].join("").as_str(), 0) {
            // Add if case for ordered list
            let mut list = Node::create_node(Some(String::from("ol")), None);
            let t = process_list_items(grapheme_vector[i..grapheme_vector.len()].to_vec(), String::from(r"\d"));
            i += t.2;
            list.children.extend(t.0);
            footnotes.children.extend(t.1);
            current_node = &list;

            root_node.children.push(list);
        } else if i+1 < grapheme_vector.len() && grapheme_vector[i..i+2].join("") == patterns.locate("image").unwrap().value {
            // Add if case for image
            let mut p = Node::create_node(Some(String::from("img")), None);
            let t = process_image(grapheme_vector[i..grapheme_vector.len()].to_vec());
            if let Some(image) = t.0 {
                root_node.children.push(image);
                i += t.1;
            }
        } else if i + 2 < grapheme_vector.len() && grapheme_vector[i..i+3].join("") == patterns.locate("codeblock").unwrap().value {
            // Add if case for code block
            let t = process_code_block(grapheme_vector[i..grapheme_vector.len()].to_vec());
            if let Some(codeblock) = t.0 {
                root_node.children.push(codeblock);
                i += t.1;
            }
        } else if (i == 0 || grapheme_vector[i - 1] == "\n") && !p_pattern.is_match(grapheme_vector[i]) {
            let mut p = Node::create_node(Some(String::from("p")), None);
            let t = process_content(grapheme_vector[i..grapheme_vector.len()].to_vec(), true);
            i += t.2;
            p.children.extend(t.0);
            footnotes.children.extend(t.1);
            current_node = &p;

            root_node.children.push(p);
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
        // TODO when whole PGS is working, invert if-else to reduce duplicate code
        let l = c[i]; // todo remove, this is debugging only
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
        } else if i < c.len() &&
            c[i..c.len()].join("").find(" ").is_some() &&
            c[i..c.len()].join("").find(" ").unwrap() > i &&
            footnote_pattern.is_match(
            c[i..c[i..c.len()].join("").find(" ").unwrap() + 1].join("").as_str()
        ) {
            // clause for footnotes
            if current_node.content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_text_node(String::new());
            }
            let r = process_footnote(c[i..c.len()].to_vec());
            if let Some(footnote) = r.0 {
                nodes.push(footnote);
                footnotes.extend(r.1);
                i += r.2;
            } else {
                i += 1;
            }
        } else if c[i] == "[" {
            // clause for links
            if current_node.content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_text_node(String::new());
            }
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
            if current_node.content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_text_node(String::new());
            }
            let r = process_image(c[i..c.len()].to_vec());
            if let Some(image) = r.0 {
                nodes.push(image);
                i += r.1;
            } else {
                i += 1;
            }
        } else if c[i] == "`" {
            if current_node.content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_text_node(String::new());
            }
            current_node = Node::create_text_node(String::new());
            // clause for italic
            let r = process_inline_code(c[i..c.len()].to_vec());
            if let Some(em) = r.0 {
                nodes.push(em);
                i += r.1;
            } else {
                i += 1; // just to be safe
            }
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

fn process_headline(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let middle_index = c[0..c.len()].join("").find(" ");
    let end_index = c[0..c.len()].join("").find("\n").unwrap_or(c.len());
    if let Some(mi) = middle_index {
        let level = c[0..mi].join("").match_indices("#").count();
        if level == mi {
            let mut headline = Node::create_node(Some(String::from(format!("h{}", level))), Some(NodeType::Node));
            let content = process_content(c[mi + 1..end_index].to_vec(), true);
            headline.children.extend(content.0);
            return (Some(headline), content.1, end_index + 1);
        } else {
            panic!();
        }
    }
    (None, vec![], 0)
}

fn process_image(c: Vec<&str>) -> (Option<Node>, usize) {
    let middle_index = c[0..c.len()].join("").find("](");
    if let Some(mi) = middle_index {
        let space_index = c[mi + 1..c.len()].join("").find(" ");
        let mut end_index = c[1..c.len()].join("").find(")");

        if space_index.is_some() && end_index.is_some() {
            let mut ei = end_index.unwrap();
            let si = space_index.unwrap() + mi + 1;
            while c[ei] != "\"" {
                if let Some(temp) = c[ei + 1..c.len()].join("").find(")") {
                    ei += temp;
                }
            }
            let mut img = Node::create_node(Some(String::from("img")), Some(NodeType::Node));
            img.attributes.insert("src".parse().unwrap(), Some(c[mi + 2..si].join("")));
            img.attributes.insert("alt".parse().unwrap(), Some(c[2..mi].join("")));
            img.attributes.insert("title".parse().unwrap(), Some(c[si + 2..ei].join("")));
            (Some(img), ei + 2)
        } else if space_index.is_none() && end_index.is_some() {
            let mut img = Node::create_node(Some(String::from("img")), Some(NodeType::Node));
            img.attributes.insert("src".parse().unwrap(), Some(c[mi + 2..end_index.unwrap() + 1].join("")));
            img.attributes.insert("alt".parse().unwrap(), Some(c[2..mi].join("")));
            (Some(img), end_index.unwrap() + 2)
        } else {
            panic!();
        }
    } else {
        (None, 0)
    }
}

fn process_link(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let middle_index = c[1..c.len()].join("").find("](");
    let end_index = c[1..c.len()].join("").find(")");
    if middle_index.is_some() && end_index.is_some() && middle_index.unwrap() < c.len() && middle_index.unwrap() < end_index.unwrap() && end_index.unwrap() < c.len() {
        let mut link_node = Node::create_node(Some(String::from("a")), Some(NodeType::Node));

        let mut mi = middle_index.unwrap() + 1;
        let mut ei = end_index.unwrap() + 1;
        loop {
            let image_middle = c[1..mi].join("").match_indices("](").count();
            let image = c[1..mi].join("").match_indices("![").count();
            if image > image_middle {
                let possible_middle = c[mi + 1..c.len()].join("").find("](");
                if let Some(val) = possible_middle {
                    mi += val + 1;
                } else {
                    panic!();
                }
                let possible_end = c[ei + 1..c.len()].join("").find(")");
                if let Some(val) = possible_end {
                    ei += val + 1;
                } else {
                    panic!();
                }
            } else {
                break;
            }
        }
        link_node.attributes.insert(String::from("href"), Some(c[mi + 2..ei].join("")));
        let r = process_content(c[1..mi].to_vec(), true);
        link_node.children.extend(r.0);
        return (Some(link_node), r.1, ei + 2);
    }
    (None, vec![], 0)
}

fn process_inline_code(c: Vec<&str>) -> (Option<Node>, usize) {
    let possible_end = c[1..c.len()].join("").find("`");
    if let Some(end) = possible_end {
        let mut code = Node::create_node(Some("code".parse().unwrap()), Some(NodeType::Node));
        let code_content = Node::create_text_node(c[1..end + 1].join(""));
        code.children.push(code_content);
        (Some(code), end + 1)
    } else {
        (None, 0)
    }
}

fn process_code_block(c: Vec<&str>) -> (Option<Node>, usize) {
    let possible_end = c[3..c.len()].join("").find("```");
    if let Some(end) = possible_end {
        let first_end_line = c.join("").find("\n");
        if first_end_line.is_none() {
            panic!();
        }
        // pre -> code
        let mut pre = Node::create_node(Some("pre".parse().unwrap()), Some(NodeType::Node));
        let mut code = Node::create_node(Some("code".parse().unwrap()), Some(NodeType::Node));
        let code_content = Node::create_text_node(c[first_end_line.unwrap()..end + 3].join("").trim().to_string());

        if c[first_end_line.unwrap()] != "\"" {
            pre.attributes.insert("class".parse().unwrap(), Some(format!("language-{}", c[3..first_end_line.unwrap()].join(""))));
            code.attributes.insert("class".parse().unwrap(), Some(format!("language-{}", c[3..first_end_line.unwrap()].join(""))));
        }

        code.children.push(code_content);
        pre.children.push(code);

        (Some(pre), end + 6)
    } else {
        (None, 0)
    }
}

fn process_footnote(c: Vec<&str>) -> (Option<Node>, Vec<Node>, usize) {
    let end_number_char = c[0..c.len()].join("").find(".").unwrap();
    let mut possible_end = end_number_char + c[end_number_char..c.len()].join("").find("]").unwrap();

    // [1. thing](address) vs [1. Abc [some](where)] vs [1. ![abc](something)]
    if possible_end + 1 < c.len() && c[possible_end + 1] == "(" && c[0..possible_end].join("").match_indices("[").count() == 0 {
        return process_link(c);
    }

    let number = c[1..end_number_char].join("");
    let mut sup = Node::create_node(Some("sup".parse().unwrap()), Some(NodeType::Node));
    let mut link = Node::create_node(Some("a".to_string()), Some(NodeType::Node));
    link.attributes.insert("href".to_string(), Some(format!("footnote-{}", number)));
    let link_content = Node::create_text_node(number);

    link.children.push(link_content);
    sup.children.push(link);

    let mut li = Node::create_node(Some("li".to_string()), Some(NodeType::Node));
    while c[0..possible_end + 1].join("").match_indices("[").count() != c[0..possible_end + 1].join("").match_indices("]").count() {
        possible_end += 1 + c[possible_end + 1..c.len()].join("").find("]").unwrap();
        let c = 3;
    }

    let footnote = process_content(c[end_number_char + 2.. possible_end].to_vec(), true);

    li.children.extend(footnote.0);

    let mut result = vec![li];
    result.extend(footnote.1);
    (Some(sup), result, possible_end + 1)
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

fn process_list_items(c: Vec<&str>, list_type: String) -> (Vec<Node>, Vec<Node>, usize) {
    let mut i = 0;
    let mut result = Vec::new();
    let mut footnotes = Vec::new();
    while i < c.len() {
        let mut next_new_line = c[i..c.len()].join("").find("\n").unwrap_or(c.len());
        if next_new_line != c.len() {
            next_new_line += i;
        }

        let mut li = Node::create_node(Some("li".to_string()), Some(NodeType::Node));
        let li_content_start = i + c[i..c.len()].join("").find(" ").unwrap() + 1;

        let mut this_level = 0;
        if next_new_line+2 < c.len() && c[next_new_line+1] == "\n" && (c[next_new_line+2] == " " || c[next_new_line+2] == "\t") {
            let mut j = next_new_line + 3;
            loop {
                if c[j] != " " && c[j] != "\t" {
                    this_level = c[next_new_line+2..j].len();
                    let next_new_line = c.join("").find("\n").unwrap_or(c.len());
                    if next_new_line == c.len() {
                        let result = parse_slothmark(c[li_content_start..c.len()].join(""));
                        li.children.extend(result.0.children);
                        footnotes.extend(result.1.children);
                        i = c.len()
                    } else {
                        if c[next_new_line+1] == "\n" && (c[next_new_line+2] == " " || c[next_new_line+2] == "\t") {

                        }
                    }
                }
            }
        } else {
            let content = process_content(c[li_content_start..next_new_line].to_vec(), true);
            li.children.extend(content.0);
            footnotes.extend(content.1);
            i += next_new_line + 1;
        }

        result.push(li);
    }
    (result, footnotes, i)
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
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].content, "Abc");
    }

    #[test]
    fn process_bold_link_content() {
        let result = process_content("[**Abc**](def)".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
    }

    #[test]
    fn process_italic_link_content() {
        let result = process_content("[*Abc*](def)".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "em");
    }

    #[test]
    fn process_bold_italic_link_content() {
        let result = process_content("[***Abc***](def)".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
    }

    #[test]
    fn process_image_link_content() {
        let result = process_content("[![Abc](def \"jkl\")](vam)".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().to_owned().unwrap();
        assert_eq!(attr, "vam");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "img");

        assert_eq!(result.0[0].children[0].attributes.contains_key("src"), true);
        let attr = result.0[0].children[0].attributes.get("src").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");

        assert_eq!(result.0[0].children[0].attributes.contains_key("title"), true);
        let attr = result.0[0].children[0].attributes.get("title").unwrap().to_owned().unwrap();
        assert_eq!(attr, "jkl");

        assert_eq!(result.0[0].children[0].attributes.contains_key("alt"), true);
        let attr = result.0[0].children[0].attributes.get("alt").unwrap().to_owned().unwrap();
        assert_eq!(attr, "Abc");
    }

    #[test]
    fn process_image_with_title_content() {
        let result = process_content("![Abc](def \"jkl\")".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "img");
        assert_eq!(result.0[0].attributes.contains_key("src"), true);
        let attr = result.0[0].attributes.get("src").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");

        assert_eq!(result.0[0].attributes.contains_key("title"), true);
        let attr = result.0[0].attributes.get("title").unwrap().to_owned().unwrap();
        assert_eq!(attr, "jkl");

        assert_eq!(result.0[0].attributes.contains_key("alt"), true);
        let attr = result.0[0].attributes.get("alt").unwrap().to_owned().unwrap();
        assert_eq!(attr, "Abc");
    }

    #[test]
    fn process_image_content() {
        let result = process_content("![Abc](def)".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "img");
        assert_eq!(result.0[0].attributes.contains_key("src"), true);
        let attr = result.0[0].attributes.get("src").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");

        assert_eq!(result.0[0].attributes.contains_key("alt"), true);
        let attr = result.0[0].attributes.get("alt").unwrap().to_owned().unwrap();
        assert_eq!(attr, "Abc");
    }

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

    #[test]
    fn process_footnote_content() {
        let result = process_content("[1. Abc]".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].name, "sup");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "a");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].content, "1");

        assert_eq!(result.1[0].children.len(), 1);
        assert_eq!(result.1[0].name, "li");
        assert_eq!(result.1[0].children[0].content, "Abc");
    }

    #[test]
    fn process_footnote_with_link_content() {
        let result = process_content("[1. Abc [abc](def)]".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].name, "sup");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "a");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].content, "1");

        println!("{:?}", result.1);
        assert_eq!(result.1.len(), 1);
        assert_eq!(result.1[0].name, "li");
        assert_eq!(result.1[0].children.len(), 2);
        assert_eq!(result.1[0].children[0].node_type, NodeType::Text);
        assert_eq!(result.1[0].children[0].content, "Abc ");
        assert_eq!(result.1[0].children[1].node_type, NodeType::Node);
        assert_eq!(result.1[0].children[1].children.len(), 1);
        assert_eq!(result.1[0].children[1].name, "a");
        assert_eq!(result.1[0].children[1].children[0].content, "abc");
    }

    #[test]
    fn process_footnote_with_image_content() {
        let result = process_content("[1. Abc ![abc](def)]".graphemes(true).collect::<Vec<&str>>(), false);
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].name, "sup");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "a");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].content, "1");

        println!("{:?}", result.1);
        assert_eq!(result.1.len(), 1);
        assert_eq!(result.1[0].name, "li");
        assert_eq!(result.1[0].children.len(), 2);
        assert_eq!(result.1[0].children[0].node_type, NodeType::Text);
        assert_eq!(result.1[0].children[0].content, "Abc ");
        assert_eq!(result.1[0].children[1].node_type, NodeType::Node);
        assert_eq!(result.1[0].children[1].name, "img");

        assert_eq!(result.1[0].children[1].attributes.contains_key("src"), true);
        let attr = result.1[0].children[1].attributes.get("src").unwrap().to_owned().unwrap();
        assert_eq!(attr, "def");

        assert_eq!(result.1[0].children[1].attributes.contains_key("alt"), true);
        let attr = result.1[0].children[1].attributes.get("alt").unwrap().to_owned().unwrap();
        assert_eq!(attr, "abc");
    }

    #[test]
    fn process_inline_code_content() {
        let result = process_content("`Abc`".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "code");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].content, "Abc");
    }

    #[test]
    fn parse_ordered_list() {
        let result = process_content("1. abc\n2. def".graphemes(true).collect::<Vec<&str>>(), false);
        println!("{:?}", result);
    }

    #[test]
    fn parse_unordered_list() {
        let result = process_content("1. abc\n2. def".graphemes(true).collect::<Vec<&str>>(), false);
        println!("{:?}", result);
    }

    #[test]
    fn parses_h1() {
        let result = parse_slothmark("# Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h1");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }

    #[test]
    fn parses_h2() {
        let result = parse_slothmark("## Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h2");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h3() {
        let result = parse_slothmark("### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h3");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h4() {
        let result = parse_slothmark("#### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h4");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h5() {
        let result = parse_slothmark("##### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h5");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h6() {
        let result = parse_slothmark("###### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h6");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }

    #[test]
    fn parses_h1_end_line() {
        let result = parse_slothmark("# Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h1");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }

    #[test]
    fn parses_h2_end_line() {
        let result = parse_slothmark("## Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h2");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h3_end_line() {
        let result = parse_slothmark("### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h3");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h4_end_line() {
        let result = parse_slothmark("#### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h4");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h5_end_line() {
        let result = parse_slothmark("##### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h5");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }
    #[test]
    fn parses_h6_end_line() {
        let result = parse_slothmark("###### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h6");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].content, "Abc");
    }

    #[test]
    fn parses_code_block() {
        let result = parse_slothmark("```\nAbc\n```".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "pre");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "code");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].content, "Abc");
    }

    #[test]
    fn parses_code_block_language() {
        let result = parse_slothmark("```css\nAbc\n```".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "pre");
        assert_eq!(result.0.children[0].attributes.contains_key("class"), true);
        let attr = result.0.children[0].attributes.get("class").unwrap().to_owned().unwrap();
        assert_eq!(attr, "language-css");
        // assert_eq!(result.0.children[0].attributes.get("class").unwrap(), "language-css");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "code");
        // assert_eq!(result.0.children[0].children[0].attributes.get("class").unwrap(), "language-css");
        assert_eq!(result.0.children[0].children[0].attributes.contains_key("class"), true);
        let attr = result.0.children[0].children[0].attributes.get("class").unwrap().to_owned().unwrap();
        assert_eq!(attr, "language-css");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].content, "Abc");
    }

    #[test]
    fn basic_unordered_list() {
        let result = parse_slothmark("- test".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].content, "test");
    }

    #[test]
    fn basic_two_items_unordered_list() {
        let result = parse_slothmark("- test\n- another".parse().unwrap());
        println!("{:?}", result);
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].content, "test");
        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].content, "another");
    }

    #[test]
    fn basic_ordered_list() {
        let result = parse_slothmark("1. test".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ol");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].content, "test");
    }

    #[test]
    fn basic_two_items_ordered_list() {
        let result = parse_slothmark("1. test\n10. another".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ol");
        assert_eq!(result.0.children[0].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].content, "test");
        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].content, "another");
    }

    #[test]
    fn basic_unordered_list_multi_line_item() {
        let result = parse_slothmark("- test\n\n  second line\n- another".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 2);

        assert_eq!(result.0.children[0].children[0].children[0].name, "p");
        assert_eq!(result.0.children[0].children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].children[0].content, "test");

        assert_eq!(result.0.children[0].children[0].children[1].name, "p");
        assert_eq!(result.0.children[0].children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[1].children[0].content, "second line");

        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].content, "another");
    }


    #[test]
    fn basic_unordered_list_multi_line_item_nested_unordered_list() {
        let result = parse_slothmark("- test\n\n  second line\n\n  - nested list\n- another".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 2);

        assert_eq!(result.0.children[0].children[0].children[0].name, "p");
        assert_eq!(result.0.children[0].children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].children[0].content, "test");

        assert_eq!(result.0.children[0].children[0].children[1].name, "p");
        assert_eq!(result.0.children[0].children[0].children[1].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].children[1].children[0].content, "second line");

        assert_eq!(result.0.children[0].children[0].children[1].children[1].name, "ul");
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children[0].content, "nested list");

        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].content, "another");
    }

    #[test]
    fn basic_unordered_list_multi_line_item_nested_ordered_list() {
        let result = parse_slothmark("- test\n\n  second line\n\n  1. nested list\n- another".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 2);

        assert_eq!(result.0.children[0].children[0].children[0].name, "p");
        assert_eq!(result.0.children[0].children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].children[0].content, "test");

        assert_eq!(result.0.children[0].children[0].children[1].name, "p");
        assert_eq!(result.0.children[0].children[0].children[1].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].children[1].children[0].content, "second line");

        assert_eq!(result.0.children[0].children[0].children[1].children[1].name, "ol");
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children[0].content, "nested list");

        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].content, "another");
    }
}

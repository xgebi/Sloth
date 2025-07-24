use std::fmt::format;
use std::thread::current;
use unicode_segmentation::UnicodeSegmentation;
// use pgs_common::node::{Node, NodeType};
use crate::patterns::Patterns;
use crate::node::Node;
use crate::node_type::NodeType;
use regex::Regex;
use crate::{Footnote};
use crate::data_type::DataType;

enum ListType {
    Ordered,
    Unordered
}

pub(crate) fn parse_slothmark(sm: String) -> (Node, Vec<Footnote>) {
    let patterns = Patterns::new();
    let processed_new_lines = sm.replace(
        patterns.locate("double_line_win").unwrap().value.as_str(),
        patterns.locate("double_line").unwrap().value.as_str()
    );
    let grapheme_vector = processed_new_lines.graphemes(true).collect::<Vec<&str>>();
    // 1. loop through sm
    let mut root_node = Node::create_by_type(NodeType::ToeRoot);
    let mut footnotes_list = vec![];
    let mut current_node = &root_node;
    let mut i: usize = 0;
    while i < grapheme_vector.len() {
        // process paragraph
        let x = grapheme_vector[i].clone();
        let p_pattern = Regex::new(patterns.locate("not_paragraph").unwrap().value.as_str()).unwrap();
        let ordered_list_regex = Regex::new(patterns.locate("ordered_list").unwrap().value.as_str()).unwrap();
        if grapheme_vector[i] == "#" {
            // case for h*
            let t = process_headline(grapheme_vector[i..grapheme_vector.len()].to_vec());
            i += t.2;
            footnotes_list.extend(t.1);
            if let Some(headline) = t.0 {
                root_node.children.push(headline);
            }
        } else if (grapheme_vector[i..i+2].join("") == patterns.locate("unordered_list").unwrap().value ||
            grapheme_vector[i..i+2].join("") == patterns.locate("unordered_list_alt").unwrap().value) && // there's a bug here for ordered lists
            ((i > 0 && grapheme_vector[i-1] == "\n") || i == 0) {
            let mut list = Node::create_normal_node("ul".to_string());

            // case for unordered list
            let mut end_of_list= grapheme_vector.len();
            let mut j = i;
            while j < grapheme_vector.len()  {
                let temp_end_of_list = grapheme_vector[j..].join("").find("\n\n");
                end_of_list = if let Some(end) = temp_end_of_list { end + j } else { grapheme_vector.len() };

                if grapheme_vector.len() > end_of_list + 4 &&
                    grapheme_vector[end_of_list + 2] == " " && grapheme_vector[end_of_list + 3] == " " {
                    j += end_of_list + 2;
                } else {
                    break;
                }
            }
            let t = process_list_items(
                grapheme_vector[i..end_of_list].to_vec(),
                String::from(grapheme_vector[i]),
                0
            );
            i = end_of_list + 2;
            list.children.extend(t.0);
            root_node.children.push(list);
            footnotes_list.extend(t.1);
        } else if ((i > 0 && grapheme_vector[i-1] == "\n") || i == 0) &&
            ordered_list_regex.is_match_at(grapheme_vector[i..grapheme_vector.len()].join("").as_str(), 0) {
            // Add if case for ordered list
            let mut list = Node::create_normal_node(String::from("ol"));
            let mut end_of_list= grapheme_vector.len();
            let mut j = i;
            while j < grapheme_vector.len()  {
                let temp_end_of_list = grapheme_vector[j..].join("").find("\n\n");
                end_of_list = if let Some(end) = temp_end_of_list { end + j } else { grapheme_vector.len() };

                if grapheme_vector.len() > end_of_list + 4 &&
                    grapheme_vector[end_of_list + 2] == " " && grapheme_vector[end_of_list + 3] == " " {
                    j += end_of_list + 2;
                } else {
                    break;
                }
            }
            let t = process_list_items(grapheme_vector[i..grapheme_vector.len()].to_vec(), String::from(r"\d"), 0);
            i = end_of_list + 2;
            list.children.extend(t.0);
            root_node.children.push(list);
            footnotes_list.extend(t.1);
        } else if i+1 < grapheme_vector.len() && grapheme_vector[i..i+2].join("") == patterns.locate("image").unwrap().value {
            // Add if case for image
            let mut p = Node::create_normal_node(String::from("img"));
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
            let mut p = Node::create_normal_node(String::from("p"));
            let t = process_content(grapheme_vector[i..grapheme_vector.len()].to_vec());
            i += t.2;
            p.children.extend(t.0);
            footnotes_list.extend(t.1);
            current_node = &p;

            root_node.children.push(p);
        } else {
            i += 1
        }
    }

    (root_node, footnotes_list)
}

fn process_content(c: Vec<&str>) -> (Vec<Node>, Vec<Footnote>, usize) {
    let patterns = Patterns::new();
    let mut i: usize = 0;
    let mut current_node = Node::create_by_type(NodeType::Text);
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
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
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
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            current_node = Node::create_by_type(NodeType::Text);
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
            footnote_pattern.is_match(
            c[i..c[i..c.len()].join("").find(" ").unwrap() + 1 + i].join("").as_str()
        ) {
            // clause for footnotes
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
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
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
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
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            let r = process_image(c[i..c.len()].to_vec());
            if let Some(image) = r.0 {
                nodes.push(image);
                i += r.1;
            } else {
                i += 1;
            }
        } else if c[i] == "`" {
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            current_node = Node::create_by_type(NodeType::Text);
            // clause for italic
            let r = process_inline_code(c[i..c.len()].to_vec());
            if let Some(em) = r.0 {
                nodes.push(em);
                i += r.1;
            } else {
                i += 1; // just to be safe
            }
        } else if c[i] != "\n" || c[i] != "\r" {
            current_node.text_content = format!("{}{}", current_node.text_content, c[i]);
            i += 1;
        } else {
            current_node.text_content = format!("{}{}", current_node.text_content, " ");
            i += 1;
        }
    }
    if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
        nodes.push(current_node);
    }
    (nodes, footnotes, c.len())
}

fn process_headline(c: Vec<&str>) -> (Option<Node>, Vec<Footnote>, usize) {
    let middle_index = c[0..c.len()].join("").find(" ");
    let end_index = c[0..c.len()].join("").find("\n").unwrap_or(c.len());
    if let Some(mi) = middle_index {
        let level = c[0..mi].join("").match_indices("#").count();
        if level == mi {
            let mut headline = Node::create_normal_node(String::from(format!("h{}", level)));
            let content = process_content(c[mi + 1..end_index].to_vec());
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
            let mut img = Node::create_normal_node(String::from("img"));
            img.attributes.insert("src".parse().unwrap(), DataType::String(c[mi + 2..si].join("")));
            img.attributes.insert("alt".parse().unwrap(), DataType::String(c[2..mi].join("")));
            img.attributes.insert("title".parse().unwrap(), DataType::String(c[si + 2..ei].join("")));
            (Some(img), ei + 2)
        } else if space_index.is_none() && end_index.is_some() {
            let mut img = Node::create_normal_node(String::from("img"));
            img.attributes.insert("src".parse().unwrap(), DataType::String(c[mi + 2..end_index.unwrap() + 1].join("")));
            img.attributes.insert("alt".parse().unwrap(), DataType::String(c[2..mi].join("")));
            (Some(img), end_index.unwrap() + 2)
        } else {
            panic!();
        }
    } else {
        (None, 0)
    }
}

fn process_link(c: Vec<&str>) -> (Option<Node>, Vec<Footnote>, usize) {
    let middle_index = c[1..c.len()].join("").find("](");
    let end_index = c[1..c.len()].join("").find(")");
    if middle_index.is_some() && end_index.is_some() && middle_index.unwrap() < c.len() && middle_index.unwrap() < end_index.unwrap() && end_index.unwrap() < c.len() {
        let mut link_node = Node::create_normal_node(String::from("a"));

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
        link_node.attributes.insert(String::from("href"), DataType::String(c[mi + 2..ei].join("")));
        let r = process_content(c[1..mi].to_vec());
        link_node.children.extend(r.0);
        return (Some(link_node), r.1, ei + 1);
    }
    (None, vec![], 0)
}

fn process_inline_code(c: Vec<&str>) -> (Option<Node>, usize) {
    let possible_end = c[1..c.len()].join("").find("`");
    if let Some(end) = possible_end {
        let mut code = Node::create_normal_node("code".to_string());
        let code_content = Node::create_text_node(c[1..end + 1].join(""));
        code.children.push(code_content);
        (Some(code), end + 2)
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
        let mut pre = Node::create_normal_node("pre".to_string());
        let mut code = Node::create_normal_node("code".to_string());
        let code_content = Node::create_text_node(c[first_end_line.unwrap()..end + 3].join("").trim().to_string());

        if c[first_end_line.unwrap()] != "\"" {
            pre.attributes.insert("class".parse().unwrap(), DataType::String(format!("language-{}", c[3..first_end_line.unwrap()].join(""))));
            code.attributes.insert("class".parse().unwrap(), DataType::String(format!("language-{}", c[3..first_end_line.unwrap()].join(""))));
        }

        code.children.push(code_content);
        pre.children.push(code);

        (Some(pre), end + 6)
    } else {
        (None, 0)
    }
}

fn process_footnote(c: Vec<&str>) -> (Option<Node>, Vec<Footnote>, usize) {
    let end_number_char = c[0..c.len()].join("").find(".").unwrap();
    let mut possible_end = end_number_char + c[end_number_char..c.len()].join("").find("]").unwrap();

    // find ]
    // check that there's not [ in between
    // if there is look for ] beyond first found
    loop {
        if c[..possible_end].join("").contains("[") {
            let count_left_bracket = c[1..possible_end].iter().filter(|c| c.contains('[')).count();
            let count_right_bracket = c[1..possible_end].iter().filter(|c| c.contains(']')).count();
            if count_left_bracket == count_right_bracket {
                break;
            }
            let local_possible_end = c[possible_end + 1..c.len()].join("").find("]").unwrap();
            possible_end = end_number_char + local_possible_end + possible_end - 1;
        }

    }

    // [1. thing](address) vs [1. Abc [some](where)] vs [1. ![abc](something)]
    if possible_end + 1 < c.len() && c[possible_end + 1] == "(" && c[0..possible_end].join("").match_indices("[").count() == 0 {
        return process_link(c);
    }

    let number = c[1..end_number_char].join("");
    let numeric_number = number.clone().parse::<isize>().unwrap();
    let mut sup = Node::create_normal_node("sup".to_string());
    let mut link = Node::create_normal_node("a".to_string());
    link.attributes.insert("href".to_string(), DataType::String(format!("footnote-{}", number)));
    let link_content = Node::create_text_node(number);

    link.children.push(link_content);
    sup.children.push(link);

    let res = process_content(c[end_number_char + 2.. possible_end].to_vec());
    let mut footnotes = res.1;
    let mut footnote_text = String::new();
    for ftn in res.0 {
        footnote_text = format!("{}{}", footnote_text, ftn.to_string());
    }
    footnotes.push(Footnote {
            text: footnote_text,
            index: numeric_number,
        });
    (Some(sup), footnotes, possible_end + 1)
}

fn process_bold(c: Vec<&str>) -> (Option<Node>, Vec<Footnote>, usize) {
    let end_index = c[2..c.len()].join("").find("**");
    match end_index {
        Some(mut i) => {
            if c[2..c.len()].join("").find("***").is_some() && c[2..c.len()].join("").find("***").unwrap() == i {
                i += 1
            }
            let mut bold = Node::create_normal_node(String::from("strong"));
            let r = process_content(c[2..i+2].to_vec());
            bold.children.extend(r.0);
            (Some(bold), r.1, i + 4)
        },
        None => {
            (None, vec![], 0)
        }
    }
}

fn process_italic(c: Vec<&str>) -> (Option<Node>, Vec<Footnote>, usize) {
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
            let mut italic = Node::create_normal_node(String::from("em"));
            let r = process_content(c[1..i+1].to_vec());
            italic.children.extend(r.0);
            (Some(italic), r.1, i + 2)
        },
        None => {
            (None, vec![], 0)
        }
    }
}

fn process_list_items(list_content: Vec<&str>, list_type: String, list_level: usize) -> (Vec<Node>, Vec<Footnote>, bool) {
    let mut i = 0;
    let mut append_to_parent = false;
    let mut result = Vec::new();
    let mut footnotes = Vec::new();
    let binding = list_content.join("").replace(
        "\n\n ",
        "<br /><br /> "
    );
    let preprocessed_list_content = binding.graphemes(true).collect::<Vec<&str>>();
    // code below should be considered as a first draft. It seems to work but(t)
    while i < preprocessed_list_content.len() {
        let mut next_new_line = preprocessed_list_content[i..].join("").find("\n").unwrap_or(preprocessed_list_content.len());
        if next_new_line != preprocessed_list_content.len() {
            next_new_line += i;
        }

        let mut li = Node::create_normal_node("li".to_string());
        let li_content_start = i + preprocessed_list_content[i..].join("").find(" ").unwrap() + 1;

        let content = process_content(preprocessed_list_content[li_content_start..next_new_line].to_vec());
        li.children.extend(content.0);
        footnotes.extend(content.1);

        let mut temp_res = vec![li];
        let mut child_list_element = "xl";
        let mut child_list = Node::create_normal_node(child_list_element.to_string());
        while preprocessed_list_content.len() > next_new_line + 1 &&
            (preprocessed_list_content[next_new_line + 1] == " " || preprocessed_list_content[next_new_line + 1] == "\t") {
            let mut space_counter = 0;
            let mut tab_counter = 0;
            let mut child_list_type = list_type.clone();

            while next_new_line + 1 + space_counter + tab_counter < preprocessed_list_content.len() {
                let counter = next_new_line + 1 + space_counter + tab_counter;
                if preprocessed_list_content[counter] == " " {
                    space_counter += 1;
                } else if preprocessed_list_content[counter] == "\t" {
                    tab_counter += 1;
                } else {
                    child_list_type = preprocessed_list_content[counter].to_string();
                    break;
                }
            }
            let level = (space_counter / 2) + tab_counter;
            if child_list_element == "xl" {
                child_list_element = if let Ok(_) = child_list_type.parse::<usize>() { "ol" } else { "ul" };
                child_list = Node::create_normal_node(child_list_element.to_string());
            }
            if list_level < level {
                let option_new_next_new_line = preprocessed_list_content[next_new_line + 1 + space_counter + tab_counter..].join("").find("\n");
                let new_next_new_line = if let Some(d) = option_new_next_new_line { d + next_new_line + 1 + space_counter + tab_counter } else { preprocessed_list_content.len() };
                let local_result = process_list_items(preprocessed_list_content[next_new_line + 1 + space_counter + tab_counter..new_next_new_line].to_owned(),
                                            child_list_type, level);
                child_list.children.extend(local_result.0);
                footnotes.extend(local_result.1);
                next_new_line = new_next_new_line;
                i = next_new_line + 1;
            }
        }
        i = next_new_line + 1;

        if child_list.children.len() > 0 {
            temp_res[0].children.push(child_list);
        }
        result.extend(temp_res);
    }
    (result, footnotes, append_to_parent)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn process_empty_content() {
        let result = process_content("".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 0);
    }

    #[test]
    fn process_paragraph_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        println!("{:?}", result);
    }

    #[test]
    fn process_link_content() {
        let result = process_content("[Abc](def)".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().clone();
        assert_eq!(attr, DataType::String("def".to_string()));
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].text_content, "Abc");
    }

    #[test]
    fn process_bold_link_content() {
        let result = process_content("[**Abc**](def)".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().clone();
        assert_eq!(attr, DataType::String("def".to_string()));
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
    }

    #[test]
    fn process_italic_link_content() {
        let result = process_content("[*Abc*](def)".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().clone();
        assert_eq!(attr, DataType::String("def".to_string()));
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "em");
    }

    #[test]
    fn process_bold_italic_link_content() {
        let result = process_content("[***Abc***](def)".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().clone();
        assert_eq!(attr, DataType::String("def".to_string()));
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
    }

    #[test]
    fn process_image_link_content() {
        let result = process_content("[![Abc](def \"jkl\")](vam)".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().clone();
        assert_eq!(attr, DataType::String("vam".to_string()));
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "img");

        assert_eq!(result.0[0].children[0].attributes.contains_key("src"), true);
        let attr = result.0[0].children[0].attributes.get("src").unwrap().clone();
        assert_eq!(attr, DataType::String("def".to_string()));

        assert_eq!(result.0[0].children[0].attributes.contains_key("title"), true);
        let attr = result.0[0].children[0].attributes.get("title").unwrap().clone();
        assert_eq!(attr, DataType::String("jkl".to_string()));

        assert_eq!(result.0[0].children[0].attributes.contains_key("alt"), true);
        let attr = result.0[0].children[0].attributes.get("alt").unwrap().clone();
        assert_eq!(attr, DataType::String("Abc".to_string()));
    }

    #[test]
    fn process_image_with_title_content() {
        let result = process_content("![Abc](def \"jkl\")".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "img");
        assert_eq!(result.0[0].attributes.contains_key("src"), true);
        let attr = result.0[0].attributes.get("src").unwrap().to_owned().clone();
        assert_eq!(attr, DataType::String("def".to_string()));

        assert_eq!(result.0[0].attributes.contains_key("title"), true);
        let attr = result.0[0].attributes.get("title").unwrap().to_owned().clone();
        assert_eq!(attr, DataType::String("jkl".to_string()));

        assert_eq!(result.0[0].attributes.contains_key("alt"), true);
        let attr = result.0[0].attributes.get("alt").unwrap().to_owned().clone();
        assert_eq!(attr, DataType::String("Abc".to_string()));
    }

    #[test]
    fn process_image_content() {
        let result = process_content("![Abc](def)".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "img");
        assert_eq!(result.0[0].attributes.contains_key("src"), true);
        let attr = result.0[0].attributes.get("src").unwrap().clone();
        assert_eq!(attr, DataType::String("def".to_string()));

        assert_eq!(result.0[0].attributes.contains_key("alt"), true);
        let attr = result.0[0].attributes.get("alt").unwrap().clone();
        assert_eq!(attr, DataType::String("Abc".to_string()));
    }

    #[test]
    fn process_italic_content() {
        let result = process_content("*Abc*".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "em");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].text_content, "Abc");
    }

    #[test]
    fn process_bold_content() {
        let result = process_content("**Abc**".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "strong");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].text_content, "Abc");
    }

    #[test]
    fn process_bold_italic_content_a() {
        let result = process_content("***Abc* def**".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "strong");
        assert_eq!(result.0[0].children.len(), 2);
        assert_eq!(result.0[0].children[0].children[0].text_content, "Abc");
        assert_eq!(result.0[0].children[0].name, "em");
        assert_eq!(result.0[0].children[1].text_content, " def");
    }

    #[test]
    fn process_bold_italic_content_b() {
        let result = process_content("*Abc **def***".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        println!("{:?}", result.0[0]);
        assert_eq!(result.0[0].name, "em");
        assert_eq!(result.0[0].children.len(), 2);
        assert_eq!(result.0[0].children[0].text_content, "Abc ".to_string());
        assert_eq!(result.0[0].children[1].name, "strong");
        assert_eq!(result.0[0].children[1].children.len(), 1);
        assert_eq!(result.0[0].children[1].children[0].text_content, "def".to_string());
    }

    #[test]
    fn process_bold_italic_content_c() {
        let result = process_content("mno *Abc **def*** jkl".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result.0[1]);
        assert_eq!(result.0.len(), 3);
        assert_eq!(result.0[0].text_content, "mno ".to_string());
        assert_eq!(result.0[1].name, "em");
        assert_eq!(result.0[1].children.len(), 2);
        assert_eq!(result.0[1].children[0].text_content, "Abc ");
        assert_eq!(result.0[1].children[1].name, "strong");
        assert_eq!(result.0[1].children[1].children.len(), 1);
        assert_eq!(result.0[1].children[1].children[0].text_content, "def");
        assert_eq!(result.0[2].text_content, " jkl".to_string());
    }

    #[test]
    fn process_bold_italic_content_d() {
        let result = process_content("*Abc **def*** jkl".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 2);
        assert_eq!(result.0[0].name, "em");
        assert_eq!(result.0[0].children.len(), 2);
        assert_eq!(result.0[0].children[0].text_content, "Abc ");
        assert_eq!(result.0[0].children[1].name, "strong");
        assert_eq!(result.0[0].children[1].children.len(), 1);
        assert_eq!(result.0[0].children[1].children[0].text_content, "def");
        assert_eq!(result.0[1].text_content, " jkl");
    }

    #[test]
    fn process_footnote_content() {
        let result = process_content("[1. Abc]".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result);
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].name, "sup");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "a");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].text_content, "1");

        // assert_eq!(result.1[0].children.len(), 1);
        // assert_eq!(result.1[0].name, "li");
        // assert_eq!(result.1[0].children[0].text_content, "Abc");
    }

    #[test]
    fn process_footnote_with_link_content() {
        let result = process_content("[1. Abc [abc](def)]".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result);
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].name, "sup");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "a");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].text_content, "1");

        println!("{:?}", result.1);
        assert_eq!(result.1.len(), 1);
        assert_eq!(result.1[0].index, 1);
        assert_eq!(result.1[0].text, "Abc <a href=\"def\">abc</a>");
    }

    #[test]
    fn process_footnote_with_image_content() {
        let result = process_content("[1. Abc ![abc](def)]".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].name, "sup");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "a");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].text_content, "1");

        println!("{:?}", result.1);
        assert_eq!(result.1.len(), 1);
        assert_eq!(result.1[0].index, 1);
        assert_eq!(result.1[0].text, "Abc <img alt=\"abc\" src=\"def\"/>");
    }
    
    // Doesn't work yet
    #[test]
    fn process_footnote_with_footnote() {
        let result = process_content("i[1. Abc[2. Def]]".graphemes(true).collect::<Vec<&str>>());
        println!("{:?}", result.1);
        // assert_eq!(result.0[0].children.len(), 1);
        // assert_eq!(result.0[0].name, "sup");
        // assert_eq!(result.0[0].children[0].children.len(), 1);
        // assert_eq!(result.0[0].children[0].name, "a");
        // assert_eq!(result.0[0].children[0].children.len(), 1);
        // assert_eq!(result.0[0].children[0].children[0].text_content, "1");
        //
        // println!("{:?}", result.1[0]);
        // assert_eq!(result.1[0].children.len(), 1);
        // assert_eq!(result.1[0].name, "li");
        // assert_eq!(result.1[0].children[0].text_content, "Abc");
    }

    #[test]
    fn process_inline_code_content() {
        let result = process_content("`Abc`".graphemes(true).collect::<Vec<&str>>());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "code");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h1() {
        let result = parse_slothmark("# Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h1");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h2() {
        let result = parse_slothmark("## Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h2");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h3() {
        let result = parse_slothmark("### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h3");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h4() {
        let result = parse_slothmark("#### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h4");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h5() {
        let result = parse_slothmark("##### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h5");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h6() {
        let result = parse_slothmark("###### Abc".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h6");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h1_end_line() {
        let result = parse_slothmark("# Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h1");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h2_end_line() {
        let result = parse_slothmark("## Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h2");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h3_end_line() {
        let result = parse_slothmark("### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h3");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h4_end_line() {
        let result = parse_slothmark("#### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h4");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h5_end_line() {
        let result = parse_slothmark("##### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h5");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h6_end_line() {
        let result = parse_slothmark("###### Abc\n".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "h6");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_code_block() {
        let result = parse_slothmark("```\nAbc\n```".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "pre");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "code");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_code_block_language() {
        let result = parse_slothmark("```css\nAbc\n```".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "pre");
        assert_eq!(result.0.children[0].attributes.contains_key("class"), true);
        let attr = result.0.children[0].attributes.get("class").unwrap().clone();
        assert_eq!(attr, DataType::String("language-css".to_string()));
        // assert_eq!(result.0.children[0].attributes.get("class").unwrap(), "language-css");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "code");
        // assert_eq!(result.0.children[0].children[0].attributes.get("class").unwrap(), "language-css");
        assert_eq!(result.0.children[0].children[0].attributes.contains_key("class"), true);
        let attr = result.0.children[0].children[0].attributes.get("class").clone();
        assert_eq!(attr.is_some(), true);
        let some_attr = attr.unwrap().clone();
        assert_eq!(some_attr, DataType::String("language-css".to_string()));
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn basic_unordered_list() {
        let result = parse_slothmark("- test".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "test");
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
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "test");
        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].text_content, "another");
    }
    
    #[test]
    fn basic_ordered_list() {
        let result = parse_slothmark("1. test".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ol");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "test");
    }
    
    #[test]
    fn basic_two_items_ordered_list() {
        let result = parse_slothmark("1. test\n10. another".parse().unwrap());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ol");
        assert_eq!(result.0.children[0].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "test");
        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].text_content, "another");
    }

    #[test]
    fn basic_two_items_two_nested_unordered_list() {
        let result = parse_slothmark("- test\n\t- nested 1\n- another\n\t- nested".parse().unwrap());
        assert_eq!(result.0.to_string(), "<ul><li>test<ul><li>nested 1</li></ul></li><li>another<ul><li>nested</li></ul></li></ul>");
    }

    #[test]
    fn basic_two_items_three_nested_unordered_list() {
        let result = parse_slothmark("- test\n\t- nested 1\n\t- nested 2\n- another\n\t- nested".parse().unwrap());
        assert_eq!(result.0.to_string(), "<ul><li>test<ul><li>nested 1</li><li>nested 2</li></ul></li><li>another<ul><li>nested</li></ul></li></ul>");
    }
    
    // doesn't work yet
    #[test]
    fn basic_unordered_list_multi_line_item() {
        let result = parse_slothmark("- test\n\n  second line\n- another".parse().unwrap());
        println!("{:?}", result.0);
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 2);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
    
        assert_eq!(result.0.children[0].children[1].name, "li");
        assert_eq!(result.0.children[0].children[1].children.len(), 1);
        assert_eq!(result.0.children[0].children[1].children[0].text_content, "another");
    }

    #[test]
    fn basic_unordered_list_multi_line_item_nested_unordered_list() {
        let result = parse_slothmark("- test\n\n  second line\n\n  - nested list\n- another".parse().unwrap());
        println!("{:?}", result.0.to_string());
        assert_eq!(result.0.children.len(), 2);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "li");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        
        //
        // assert_eq!(result.0.children[0].children[0].children[1].children[1].name, "ul");
        // assert_eq!(result.0.children[0].children[0].children[1].children[1].children.len(), 1);
        // assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].name, "li");
        // assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children.len(), 1);
        // assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children[0].text_content, "nested list");

        // assert_eq!(result.0.children[0].children[1].name, "li");
        // assert_eq!(result.0.children[0].children[1].children.len(), 1);
        // assert_eq!(result.0.children[0].children[1].children[0].text_content, "another");
    }

    // #[test]
    // fn basic_unordered_list_multi_line_item_nested_ordered_list() {
    //     let result = parse_slothmark("- test\n\n  second line\n\n  1. nested list\n- another".parse().unwrap());
    //     assert_eq!(result.0.children.len(), 1);
    //     assert_eq!(result.0.children[0].name, "ul");
    //     assert_eq!(result.0.children[0].children.len(), 2);
    //     assert_eq!(result.0.children[0].children[0].name, "li");
    //     assert_eq!(result.0.children[0].children[0].children.len(), 2);
    //
    //     assert_eq!(result.0.children[0].children[0].children[0].name, "p");
    //     assert_eq!(result.0.children[0].children[0].children[0].children.len(), 1);
    //     assert_eq!(result.0.children[0].children[0].children[0].children[0].text_content, "test");
    //
    //     assert_eq!(result.0.children[0].children[0].children[1].name, "p");
    //     assert_eq!(result.0.children[0].children[0].children[1].children.len(), 2);
    //     assert_eq!(result.0.children[0].children[0].children[1].children[0].text_content, "second line");
    //
    //     assert_eq!(result.0.children[0].children[0].children[1].children[1].name, "ol");
    //     assert_eq!(result.0.children[0].children[0].children[1].children[1].children.len(), 1);
    //     assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].name, "li");
    //     assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children.len(), 1);
    //     assert_eq!(result.0.children[0].children[0].children[1].children[1].children[0].children[0].text_content, "nested list");
    //
    //     assert_eq!(result.0.children[0].children[1].name, "li");
    //     assert_eq!(result.0.children[0].children[1].children.len(), 1);
    //     assert_eq!(result.0.children[0].children[1].children[0].text_content, "another");
    // }
}

#[cfg(test)]
mod rw_test {
    use crate::slothmark::parse_slothmark;

    #[test]
    fn test_inline_code_in_text() {
        let text = r#"where `a = 1` and `z = 26`. Fortunately"#;
        let result = parse_slothmark(text.to_string());
        println!("{}", result.0.to_string());
        let expected = r#"<p>where <code>a = 1</code> and <code>z = 26</code>. Fortunately</p>"#;
        assert_eq!(result.0.to_string(), expected);
    }

    #[test]
    fn test_code_block_with_text_after() {
        let text = r#"```
Changing the behavior of elements like that based on context
is anti-pattern in our opinion and should be discouraged.
```

For"#;
        let result = parse_slothmark(text.to_string());
        println!("{}", result.0.to_string());
        let expected = r#"<pre class="language-"><code class="language-">Changing the behavior of elements like that based on context
is anti-pattern in our opinion and should be discouraged.</code></pre><p>
For</p>"#;
        assert_eq!(result.0.to_string(), expected);
    }

    #[test]
    fn debug_real() {
        let text = r#"I'll let [Ryosuke Niva explain](https://bugs.webkit.org/show_bug.cgi?id=160038#c3) [1. Nothing has changed in [six years](https://bugs.webkit.org/show_bug.cgi?id=249319#c3)]:"#;
        let result = parse_slothmark(text.to_string());
        println!("{}", result.0.to_string());
        let expected = r#"<p>I'll let <a href="https://bugs.webkit.org/show_bug.cgi?id=160038#c3">Ryosuke Niva explain</a> <sup><a href="footnote-1">1</a></sup>:</p>"#;
        assert_eq!(result.0.to_string(), expected);
        assert_eq!(result.1.len(), 1);
    }
}

use unicode_segmentation::UnicodeSegmentation;
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
    let mut processed_new_lines = sm.replace(
        patterns.locate("double_line_win").unwrap().value.as_str(),
        patterns.locate("double_line").unwrap().value.as_str()
    );
    processed_new_lines = processed_new_lines.replace(
        "’",
        "'"
    );
    // processed_new_lines = processed_new_lines.replace(
    //     " ",
    //     " "
    // );
    // ’  
    let grapheme_vector = processed_new_lines.graphemes(true).collect::<Vec<&str>>();
    // 1. loop through sm
    let mut root_node = Node::create_by_type(NodeType::ToeRoot);
    let mut footnotes_list = vec![];

    let t = process_content(grapheme_vector.to_vec(), true);
    root_node.children.extend(t.0);
    footnotes_list.extend(t.1);

    (root_node, footnotes_list)
}

fn process_content(c: Vec<&str>, create_paragraph: bool) -> (Vec<Node>, Vec<Footnote>, usize) {
    let patterns = Patterns::new();
    let mut i: usize = 0;
    let mut current_node = Node::create_by_type(NodeType::Text);
    let mut nodes = Vec::new();
    let mut inline_nodes = Vec::new();
    let mut footnotes = Vec::new();
    let footnote_pattern = Regex::new(patterns.locate("footnote").unwrap().value.as_str()).unwrap();
    let ordered_list_regex = Regex::new(patterns.locate("ordered_list").unwrap().value.as_str()).unwrap();
    let j = c.len();
    let mut stuck_index = 0;
    while i < j {
        let l = c[i]; // todo remove, this is debugging only
        // unordered list
        if stuck_index == i && i > 0 {
            print!("stuck")
        } else {
            stuck_index = i;
        }
        if c.len() > i + 2 && (c[i..i+2].join("") == patterns.locate("unordered_list").unwrap().value ||
            c[i..i+2].join("") == patterns.locate("unordered_list_alt").unwrap().value) && // there's a bug here for ordered lists
            ((i > 0 && c[i-1] == "\n") || i == 0) {
            let mut list = Node::create_normal_node("ul".to_string());

            // case for unordered list
            let mut end_of_list= c.len();
            let mut j = i;
            while j < c.len()  {
                let temp_end_of_list = c[j..].join("").find("\n\n");
                end_of_list = if let Some(end) = temp_end_of_list { end + j } else { c.len() };

                if c.len() > end_of_list + 4 &&
                    c[end_of_list + 2] == " " && c[end_of_list + 3] == " " {
                    j += end_of_list + 2;
                } else {
                    break;
                }
            }
            let t = process_list_items(
                c[i..end_of_list].to_vec(),
                String::from(c[i]),
                0
            );
            i = end_of_list;
            list.children.extend(t.0);
            nodes.push(list);
            footnotes.extend(t.1);
        // ordered list
        } else if ((i > 0 && c[i-1] == "\n") || i == 0) &&
            ordered_list_regex.is_match_at(c[i..c.len()].join("").as_str(), 0) {
            // Add if case for ordered list
            let mut list = Node::create_normal_node(String::from("ol"));
            let mut end_of_list= c.len();
            let mut j = i;
            while j < c.len()  {
                let temp_end_of_list = c[j..].join("").find("\n\n");
                end_of_list = if let Some(end) = temp_end_of_list { end + j } else { c.len() };

                if c.len() > end_of_list + 4 &&
                    c[end_of_list + 2] == " " && c[end_of_list + 3] == " " {
                    j += end_of_list + 2;
                } else {
                    break;
                }
            }
            let t = process_list_items(c[i..c.len()].to_vec(), String::from(r"\d"), 0);
            i = end_of_list + 2;
            list.children.extend(t.0);
            nodes.push(list);
            footnotes.extend(t.1);
        // headline
        } else if c[i] == "#" && (i == 0 || c[i - 1] == "\n") {
            // case for h*
            let t = process_headline(c[i..c.len()].to_vec());
            i += t.2;
            footnotes.extend(t.1);
            if let Some(headline) = t.0 {
                nodes.push(headline);
            }
        // bold text
        } else if i+2 < c.len() && c[i..i+2].join("") == "**" {
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                inline_nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            // clause for bold
            let r = process_bold(c[i..c.len()].to_vec());
            if let Some(strong) = r.0 {
                inline_nodes.push(strong);
                footnotes.extend(r.1);
                i += r.2;
            } else {
                i += 1; // just to be safe
            }
        // italic text
        } else if c[i] == "*" {
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                inline_nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            current_node = Node::create_by_type(NodeType::Text);
            // clause for italic
            let r = process_italic(c[i..c.len()].to_vec());
            // current_node.children.push(r.0.unwrap());
            if let Some(em) = r.0 {
                inline_nodes.push(em);
                footnotes.extend(r.1);
                i += r.2;
            } else {
                i += 1; // just to be safe
            }
        // footnotes
        } else if i < c.len() &&
            c[i..c.len()].join("").find(" ").is_some() &&
            footnote_pattern.is_match(
            c[i..c[i..c.len()].join("").find(" ").unwrap() + 1 + i].join("").as_str()
        ) {
            // clause for footnotes
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                inline_nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            let r = process_footnote(c[i..c.len()].to_vec());
            if let Some(footnote) = r.0 {
                inline_nodes.push(footnote);
                footnotes.extend(r.1);
                i += r.2;
            } else {
                i += 1;
            }
        // links
        } else if c[i] == "[" {
            // clause for links
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                inline_nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            let middle_index = c[i + 1..c.len()].join("").find("](");
            if middle_index.is_some() && c[i + 1..middle_index.unwrap() + i].join("").match_indices("]").count() > 0 {
                let end = i + 2 + c[i + 1..middle_index.unwrap() + i].join("").find("]").unwrap();
                let r = process_content(c[i + 1..end - 1].to_vec(), false);
                let start_node = Node::create_text_node(String::from("["));
                let end_node = Node::create_text_node(String::from("]"));
                inline_nodes.push(start_node);
                inline_nodes.extend(r.0);
                inline_nodes.push(end_node);
                footnotes.extend(r.1);
                i += r.2 + 2;
            } else {
                let r = process_link(c[i..c.len()].to_vec());
                if let Some(link) = r.0 {
                    inline_nodes.push(link);
                    footnotes.extend(r.1);
                    i += r.2;
                } else {
                    i += 1;
                }
            }
        // image
        } else if i+1 < c.len() && c[i..i+2].join("") == patterns.locate("image").unwrap().value {
            // clause for images
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                inline_nodes.push(current_node);
                current_node = Node::create_by_type(NodeType::Text);
            }
            let r = process_image(c[i..c.len()].to_vec());
            if let Some(image) = r.0 {
                inline_nodes.push(image);
                i += r.1;
            } else {
                i += 1;
            }
        // code
        } else if c[i] == "`" {
            if c.len() > i + 2 && c[i+1]  == "`" && c[i+2]  == "`" {
                // Add if case for code block
                let t = process_code_block(c[i..c.len()].to_vec());
                if let Some(codeblock) = t.0 {
                    nodes.push(codeblock);
                    i += t.1;
                }
            } else {
                if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                    inline_nodes.push(current_node);
                    current_node = Node::create_by_type(NodeType::Text);
                }
                current_node = Node::create_by_type(NodeType::Text);
                // clause for italic
                let r = process_inline_code(c[i..c.len()].to_vec());
                if let Some(em) = r.0 {
                    inline_nodes.push(em);
                    i += r.1;
                } else {
                    i += 1; // just to be safe
                }
            }
        } else if c[i] != "\n" && c[i] != "\r" {
            let formatted = format!("{}{}", current_node.text_content, c[i]);
            current_node.text_content = formatted.clone();

            if (c.len() == i + 1 && !formatted.trim().is_empty()) && create_paragraph {
                let mut p = Node::create_normal_node(String::from("p"));
                p.children.extend(inline_nodes.clone());
                p.children.push(current_node.clone());
                nodes.push(p);
                current_node = Node::create_by_type(NodeType::Text);
                inline_nodes = Vec::new();
            }
            i += 1;
        } else if (c.len() > i + 1 && c[i] == "\n" && c[i + 1] == "\n") || c.len() == i + 1  {
            if current_node.text_content.len() > 0 || current_node.children.len() > 0 {
                let mut p = Node::create_normal_node(String::from("p"));
                p.children.extend(inline_nodes.clone());
                p.children.push(current_node.clone());
                nodes.push(p);
                inline_nodes = Vec::new();
            }
            current_node = Node::create_by_type(NodeType::Text);
            i += 2
        } else {
            current_node.text_content = format!("{}{}", current_node.text_content, " ");
            i += 1;
        }
    }
    if inline_nodes.is_empty() && (current_node.text_content.len() > 0 || current_node.children.len() > 0) {
        nodes.push(current_node);
    } else if !inline_nodes.is_empty() && create_paragraph {
        let mut p = Node::create_normal_node(String::from("p"));
        p.children.extend(inline_nodes);
        if current_node.text_content.len() > 0 {
            p.children.push(current_node);
        }
        nodes.push(p);
    } else if !inline_nodes.is_empty() && !create_paragraph {
        nodes.extend(inline_nodes);
        if current_node.text_content.len() > 0 {
            nodes.push(current_node);
        }
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
            let content = process_content(c[mi + 1..end_index].to_vec(), false);
            headline.children.extend(content.0);
            let end_trail = if c.len() > end_index + 1 && c[end_index + 1] == "\n" { 2 } else { 1 };
            return (Some(headline), content.1, end_index + end_trail);
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
    let mut middle_index = 0;
    let mut end_index = 0;
    let mut i = 1;
    while i < c.len() {
        if c[i] == "]" && c.len() > i + 1 && c[i+1] == "(" {
            middle_index = i;
        }
        if c[i] == ")" && middle_index > end_index {
            end_index = i;
            break;
        }
        i+= 1;
    }
    if middle_index < end_index && middle_index < c.len() && middle_index < end_index && end_index < c.len() {
        let mut link_node = Node::create_normal_node(String::from("a"));

        let mut mi = middle_index;
        let mut ei = end_index;
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
        let r = process_content(c[1..mi].to_vec(), false);
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
    let mut end = 4;
    loop {
        end += 1;
        if c.len() > end + 2 && c[end] == "`" && c[end + 1] == "`" && c[end + 2] == "`" {
            break;
        }
        if c.len() == end + 1 {
            panic!();
        }
    }

    let first_end_line = c.join("").find("\n");
    if first_end_line.is_none() {
        panic!();
    }
    // pre -> code
    let mut pre = Node::create_normal_node("pre".to_string());
    let mut code = Node::create_normal_node("code".to_string());
    let code_content_text = c[first_end_line.unwrap() + 1..end].join("").to_string();
    let code_content = Node::create_text_node(code_content_text.clone());

    if c[first_end_line.unwrap()] != "\"" {
        pre.attributes.insert("class".parse().unwrap(), DataType::String(format!("language-{}", c[3..first_end_line.unwrap()].join(""))));
        code.attributes.insert("class".parse().unwrap(), DataType::String(format!("language-{}", c[3..first_end_line.unwrap()].join(""))));
    }

    code.children.push(code_content);
    pre.children.push(code);

    let movement = end + 3;

    (Some(pre), movement)
}

fn process_footnote(c: Vec<&str>) -> (Option<Node>, Vec<Footnote>, usize) {
    let end_number_char = c[0..c.len()].join("").find(".").unwrap();
    let mut possible_end = 1;
    let mut i = 1;
    let mut opening_counter = 0;
    let mut closing_counter = 0;
    while i < c.len() {
        if c[i] == "]" && opening_counter == closing_counter {
            possible_end = i;
            break;
        }
        if c[i] == "[" {
            opening_counter += 1;
        }
        if c[i] == "]" {
            closing_counter += 1;
        }
        i+=1;
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

    let res = process_content(c[end_number_char + 2.. possible_end].to_vec(), false);
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
            let r = process_content(c[2..i+2].to_vec(), false);
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
            let r = process_content(c[1..i+1].to_vec(), false);
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
        let mut next_new_line = i;
        let mut j = i + 1;
        while j < preprocessed_list_content.len() {
            if preprocessed_list_content[j] == "\n" {
                next_new_line = j;
                break;
            }
            j += 1;
            if j == preprocessed_list_content.len() {
                next_new_line = j;
            }
        }

        let mut li = Node::create_normal_node("li".to_string());
        let li_content_start = i + preprocessed_list_content[i..].join("").find(" ").unwrap_or(preprocessed_list_content.len()) + 1;
        if li_content_start > next_new_line {
            break;
        }

        let content = process_content(preprocessed_list_content[li_content_start..next_new_line].to_vec(), false);
        li.children.extend(content.0);
        footnotes.extend(content.1);

        let mut temp_res = vec![li];
        let mut child_list_element = "xl";
        let mut child_list = Node::create_normal_node(child_list_element.to_string());
        if preprocessed_list_content.len() > next_new_line + 1 && (preprocessed_list_content[next_new_line + 1] == " " || preprocessed_list_content[next_new_line + 1] == "\t") {
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
        }
        i = next_new_line;

        if child_list.children.len() > 0 {
            temp_res[0].children.push(child_list);
        }
        result.extend(temp_res);
        if (i + 1 < preprocessed_list_content.len() && preprocessed_list_content[i] == "\n"  && preprocessed_list_content[i + 1] == "\n") {
            return (result, footnotes, append_to_parent);
        }
    }
    (result, footnotes, append_to_parent)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn process_empty_content() {
        let result = process_content("".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 0);
    }

    #[test]
    fn process_paragraph_content() {
        let result = process_content("Abc".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        println!("{:?}", result);
    }

    #[test]
    fn process_link_content() {
        let result = process_content("[Abc](def)".graphemes(true).collect::<Vec<&str>>(), false);
        println!("{:?}", result.0[0].to_string());
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
        let result = process_content("[**Abc**](def)".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("[*Abc*](def)".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("[***Abc***](def)".graphemes(true).collect::<Vec<&str>>(), false);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "a");
        assert_eq!(result.0[0].attributes.contains_key("href"), true);
        let attr = result.0[0].attributes.get("href").unwrap().clone();
        assert_eq!(attr, DataType::String("def".to_string()));
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
    }

    // TODO consider create paragraph to true
    #[test]
    fn process_image_link_content() {
        let result = process_content("[![Abc](def \"jkl\")](vam)".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("![Abc](def \"jkl\")".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("![Abc](def)".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("*Abc*".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "p");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "em");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn process_bold_content() {
        let result = process_content("**Abc**".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "p");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn process_bold_italic_content_a() {
        let result = process_content("***Abc* def**".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0[0].to_string());
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "p");
        println!("{:?}", result.0[0].children[0].to_string());
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "strong");
        assert_eq!(result.0[0].children[0].children.len(), 2);
        assert_eq!(result.0[0].children[0].children[0].children[0].text_content, "Abc");
        assert_eq!(result.0[0].children[0].children[0].name, "em");
        assert_eq!(result.0[0].children[0].children[1].text_content, " def");
    }

    #[test]
    fn process_bold_italic_content_b() {
        let result = process_content("*Abc **def***".graphemes(true).collect::<Vec<&str>>(), true);
        println!("{:?}", result.0);
        assert_eq!(result.0.len(), 1);
        println!("{:?}", result.0[0]);
        assert_eq!(result.0[0].name, "p");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "em");
        assert_eq!(result.0[0].children[0].children.len(), 2);
        assert_eq!(result.0[0].children[0].children[0].text_content, "Abc ".to_string());
        assert_eq!(result.0[0].children[0].children[1].name, "strong");
        assert_eq!(result.0[0].children[0].children[1].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[1].children[0].text_content, "def".to_string());
    }

    #[test]
    fn process_bold_italic_content_c() {
        let result = process_content("mno *Abc **def*** jkl".graphemes(true).collect::<Vec<&str>>(), false);
        println!("{:?}", result.0);
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
        let result = process_content("*Abc **def*** jkl".graphemes(true).collect::<Vec<&str>>(), false);
        println!("{:?}", result.0);
        println!("{:?}", result.0[0].to_string());
        println!("{:?}", result.0[1].to_string());
        assert_eq!(result.0.len(), 2);
        assert_eq!(result.0[0].name, "em");
        assert_eq!(result.0[0].children.len(), 2);
        assert_eq!(result.0[0].children[0].text_content, "Abc ");
        assert_eq!(result.0[0].children[1].name, "strong");
        assert_eq!(result.0[0].children[1].children.len(), 1);
        assert_eq!(result.0[0].children[1].children[0].text_content, "def");
        assert_eq!(result.0[1].text_content, " jkl");
    }

    // TODO consider create paragraph to true
    #[test]
    fn process_footnote_content() {
        let result = process_content("[1. Abc]".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("[1. Abc [abc](def)]".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("[1. Abc ![abc](def)]".graphemes(true).collect::<Vec<&str>>(), false);
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
        let result = process_content("i[1. Abc[2. Def]]".graphemes(true).collect::<Vec<&str>>(), true);
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
        let result = process_content("`Abc`".graphemes(true).collect::<Vec<&str>>(), true);
        assert_eq!(result.0.len(), 1);
        assert_eq!(result.0[0].name, "p");
        assert_eq!(result.0[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].name, "code");
        assert_eq!(result.0[0].children[0].children.len(), 1);
        assert_eq!(result.0[0].children[0].children[0].text_content, "Abc");
    }

    #[test]
    fn parses_h1() {
        let result = parse_slothmark("# Abc".parse().unwrap());
        println!("{:?}", result.0);
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
        println!("{:?}", result.0.to_string());
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "pre");
        assert_eq!(result.0.children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].name, "code");
        assert_eq!(result.0.children[0].children[0].children.len(), 1);
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "Abc\n");
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
        assert_eq!(result.0.children[0].children[0].children[0].text_content, "Abc\n");
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
        println!("{:?}", result.0);
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
        assert_eq!(result.0.children.len(), 1);
        assert_eq!(result.0.children[0].name, "ul");
        assert_eq!(result.0.children[0].children.len(), 2);
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
is anti-pattern in our opinion and should be discouraged.
</code></pre><p>For</p>"#;
        assert_eq!(result.0.to_string(), expected);
    }

    #[test]
    fn test_footnote_with_link() {
        let text = r#"I'll let [Ryosuke Niva explain](https://bugs.webkit.org/show_bug.cgi?id=160038#c3) [1. Nothing has changed in [six years](https://bugs.webkit.org/show_bug.cgi?id=249319#c3)]:"#;
        let result = parse_slothmark(text.to_string());
        println!("{}", result.0.to_string());
        let expected = r#"<p>I'll let <a href="https://bugs.webkit.org/show_bug.cgi?id=160038#c3">Ryosuke Niva explain</a> <sup><a href="footnote-1">1</a></sup>:</p>"#;
        assert_eq!(result.0.to_string(), expected);
        assert_eq!(result.1.len(), 1);
    }

    #[test]
    fn test_headline_after_ordered_list() {
        let text = r#"1. I

## I"#;

        let result = parse_slothmark(text.to_string());
        println!("{}", result.0.to_string());
        assert_eq!(result.0.to_string(), r#"<ol><li>I</li></ol><h2>I</h2>"#)
    }

    #[test]
    fn test_unordered_list() {
        let text = r#"T:

- `Inf`
- `-Inf`"#;

        let result = parse_slothmark(text.to_string());
        println!("{}", result.0.to_string());
        assert_eq!(result.0.to_string(), r#"<p>T:</p><ul><li><code>Inf</code></li><li><code>-Inf</code></li></ul>"#)
    }

    #[test]
    fn test_link_with_apostrophe() {
        let text = r#"[Link with ’](https://example.com)"#;
        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        assert_eq!(result.0.to_string(), r#"<p><a href="https://example.com">Link with '</a></p>"#);
    }

    #[test]
    fn test_link_with_apostrophe_2() {
        let text = r#"[Link with you’ve](https://example.com)"#;
        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        assert_eq!(result.0.to_string(), r#"<p><a href="https://example.com">Link with you've</a></p>"#)
    }

    #[test]
    fn test_list_after_headline() {
        let text = r#"- Parent
        - [One link’s apostrophe](https://example.com)
        - [Second link’s apostrophe](https://example.com)

## Personal

I"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<ul><li>Parent<ul><li><a href="https://example.com">One link's apostrophe</a></li><li><a href="https://example.com">Second link's apostrophe</a></li></ul></li></ul><h2>Personal</h2><p>I</p>"#;
        assert_eq!(str_res.contains("Personal"), true);
        assert_eq!(str_res, expected);
    }


    #[test]
    fn test_square_brackets() {
        let text = r#"<table>
<tbody>
<tr>
<td>[&#39;gluten-free&#39;]</td>
</tr>
</tbody>
</table>

## Resources

- [abc](https://example.com)"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
    }

    #[test]
    fn test_table_in_pre() {
        let text = r#"```
                 post                 |    is_empty     
--------------------------------------+-----------------
 ff095bf4-63bf-4059-beff-74ac085c616c | empty
```

## Resources

- [CASE expression documentation](https://www.postgresql.org/docs/17/functions-conditional.html#FUNCTIONS-CASE)
- [StackOverflow answer about quotes](https://stackoverflow.com/a/7651432)"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<pre class="language-"><code class="language-">                 post                 |    is_empty     
--------------------------------------+-----------------
 ff095bf4-63bf-4059-beff-74ac085c616c | empty
</code></pre><h2>Resources</h2><ul><li><a href="https://www.postgresql.org/docs/17/functions-conditional.html#FUNCTIONS-CASE">CASE expression documentation</a></li><li><a href="https://stackoverflow.com/a/7651432">StackOverflow answer about quotes</a></li></ul>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_list_after_codeblock() {
        let text = r#"```
 
```

- [CASE expression documentation](https://www.postgresql.org/docs/17/functions-conditional.html#FUNCTIONS-CASE)
- [StackOverflow answer about quotes](https://stackoverflow.com/a/7651432)"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<pre class="language-"><code class="language-"> 
</code></pre><ul><li><a href="https://www.postgresql.org/docs/17/functions-conditional.html#FUNCTIONS-CASE">CASE expression documentation</a></li><li><a href="https://stackoverflow.com/a/7651432">StackOverflow answer about quotes</a></li></ul>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_two_codeblocks() {
        let text = r#"```CSS
a { display: block; }
```
```CSS
b { display: inline; }
```"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<pre class="language-CSS"><code class="language-CSS">a { display: block; }
</code></pre><pre class="language-CSS"><code class="language-CSS">b { display: inline; }
</code></pre> "#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_three_paragraphs() {
        let text = r#"First

Second

Third"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<p>First</p><p>Second</p><p>Third</p>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_math_2() {
        let text = r#"```HTML
∫
```"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<pre class="language-HTML"><code class="language-HTML">∫
</code></pre>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_math_1() {
        let text = r#"```HTML
∫
```
```CSS
.a {
	math-style: compact;
}
```"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<pre class="language-HTML"><code class="language-HTML">∫
</code></pre><pre class="language-CSS"><code class="language-CSS">.a {
	math-style: compact;
}
</code></pre> "#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_weird_chars() {
        let text = r#"∫

```HTML
∫
```

```CSS
.example-math-style-normal {
	math-style: normal;
}
```
"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<p>∫</p><pre class="language-HTML"><code class="language-HTML">∫
</code></pre><pre class="language-CSS"><code class="language-CSS">.example-math-style-normal {
	math-style: normal;
}
</code></pre>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_compound_paragraph() {
        let text = r#"The `compact`.

<section>This is a text with a formula <math class="example-math-style-compact"><mrow><msubsup><mo movablelimits="false">∫</mo><mi>a</mi><mi>b</mi></msubsup><msup><mi>x</mi><mn>2</mn></msup><mspace width="0.1667em"></mspace><mi>d</mi><mi>x</mi></mrow>
  </math> inside it because it is relevant.</section>"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<p>The <code>compact</code>.</p><p><section>This is a text with a formula <math class="example-math-style-compact"><mrow><msubsup><mo movablelimits="false">∫</mo><mi>a</mi><mi>b</mi></msubsup><msup><mi>x</mi><mn>2</mn></msup><mspace width="0.1667em"></mspace><mi>d</mi><mi>x</mi></mrow>   </math> inside it because it is relevant.</section></p>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_footnote() {
        let text = r#"Cs[1. Alois Rašín by Jana Čechurová, CPress 2023], "#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<p>Cs<sup><a href="footnote-1">1</a></sup>, </p>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_link_in_list() {
        let text = r#"- [Ein Artikel über web Scraping in JS](https://www.scrapingbee.com/blog/web-scraping-javascript/#jsdom-the-dom-for-node)"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<ul><li><a href="https://www.scrapingbee.com/blog/web-scraping-javascript/#jsdom-the-dom-for-node">Ein Artikel über web Scraping in JS</a></li></ul>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_german_resources() {
        let text = r#"## Ressourcen

- [Ein Artikel über web Scraping in JS](https://www.scrapingbee.com/blog/web-scraping-javascript/#jsdom-the-dom-for-node)
- [JSDOM Bibliothek](https://github.com/jsdom/jsdom#readme)
- [Ein Artikel über Web scraping auf freeCodeCamp](https://www.freecodecamp.org/news/scraping-wikipedia-articles-with-python/)
- [BeautifulSoup Dokumentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Ein Artikel auf ProWebScriper über Bibliotheken in Python](https://prowebscraper.com/blog/best-web-scraping-libraries-in-python/)"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<h2>Ressourcen</h2><ul><li><a href="https://www.scrapingbee.com/blog/web-scraping-javascript/#jsdom-the-dom-for-node">Ein Artikel über web Scraping in JS</a></li><li><a href="https://github.com/jsdom/jsdom#readme">JSDOM Bibliothek</a></li><li><a href="https://www.freecodecamp.org/news/scraping-wikipedia-articles-with-python/">Ein Artikel über Web scraping auf freeCodeCamp</a></li><li><a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/">BeautifulSoup Dokumentation</a></li><li><a href="https://prowebscraper.com/blog/best-web-scraping-libraries-in-python/">Ein Artikel auf ProWebScriper über Bibliotheken in Python</a></li></ul>"#;
        assert_eq!(str_res, expected);
    }

    #[test]
    fn test_real() {
        let text = r#"The reason into looking at the cooking times is that making food for me is a bit stressful activity. Too many things are going on at the same time and knowing which recipes are doable for me is important as my [spoons](https://en.wikipedia.org/wiki/Spoon_theory) are limited.

Note: assumption is that the dataset is saved in variable called `recipes`.

Let's look first at the total time of cooking because preparation and actual cooking often go one after another. There are exceptions like overnight marinading the meat but other than that we want to cook with freshly prepared ingredients.

To do that in Python we use pandas and add the two columns together. Following code won't add a new column to the recipes table, it'll create a standalone [Series](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html) object:

```Python
import pandas

total_cooking_time = recipes['cooking_time_minutes'] + recipes['prep_time_minutes']
```

To take a look at the data let's use a histogram. In the chart below there's a basic Seaborn histogram with default options. From this we can see that quite a few recipes have total cooking time around an hour and two recipes take longer than 8 hours to make.

<img src="https://www.sarahgebauer.com/sloth-content/2025/4/total_cooking.png" alt="Histogram with cooking times" />

To take a look at the two outliers we can query with pandas:

```Python
recipes[recipes['cooking_time_minutes'] >= 480]
```

<table>
<thead>
<tr>
<th>recipe_name</th>
<th>cuisine</th>
<th>ingredients</th>
<th>cooking_time_minutes</th>
<th>prep_time_minutes</th>
<th>servings</th>
<th>calories_per_serving</th>
<th>dietary_restrictions</th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td>30</td>
<td>Swedish Gravlax with Dill Sauce</td>
<td>Swedish</td>
<td>[&#39;Salmon fillet&#39;, &#39;Salt&#39;, &#39;Sugar&#39;, &#39;White pepp...</td>
<td>720</td>
<td>30</td>
<td>8.0</td>
<td>250.0</td>
<td>[&#39;gluten-free&#39;, &#39;dairy-free&#39;]</td>
</tr>
<tr>
<td>81</td>
<td>Hawaiian Kalua Pig (Slow-Cooked Shredded Pork)</td>
<td>Polynesian</td>
<td>[&#39;Pork shoulder&#39;, &#39;Liquid smoke (optional)&#39;, &#39;...</td>
<td>480</td>
<td>15</td>
<td>8.0</td>
<td>400.0</td>
<td>[&#39;gluten-free&#39;, &#39;dairy-free&#39;]</td>
</tr>
</tbody>
</table>

We can also try to do a bit more granular histogram but it won't reveal much more. Histogram with bin size of 5 looks like this:

<img src="https://www.sarahgebauer.com/sloth-content/2025/4/total_cooking_5min.png" alt="Histogram with cooking times with 5 minute bins" />

As I'd like to eat something and sinc dealing with heat can be more stressful than than the preparation, so let's look at the recipes which have same or shorter cooking time than prep time. We can do this with:

```Python
recipes[recipes['prep_time_minutes'] >= recipes['cooking_time_minutes']]
```

Depending on when the dataset was updated, it will result in 21 recipes. Some of them look doable.
## Resources

- [Data set on Kaggle](https://www.kaggle.com/datasets/prajwaldongre/collection-of-recipes-around-the-world/)"#;

        let result = parse_slothmark(text.to_string());
        let str_res = result.0.to_string();
        println!("{}", str_res);
        let expected = r#"<pre class="language-CSS"><code class="language-CSS">a { display: block; }</code></pre><pre class="language-CSS"><code class="language-CSS">b { display: inline; }</code></pre>
"#;
        assert_eq!(str_res, expected);
    }
}

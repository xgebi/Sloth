use std::collections::HashMap;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use pgs_common::patterns::{Pattern, Patterns};

fn parse_toe(sm: String) -> Result<Node, ()> {
    let patterns = Patterns::new();
    let processed_new_lines = sm.replace(
        patterns.locate("double_line_win").unwrap().value.as_str(),
        patterns.locate("double_line").unwrap().value.as_str()
    );
    let grapheme_vector = processed_new_lines.graphemes(true).collect::<Vec<&str>>();
    process_nodes(grapheme_vector)
}

fn process_nodes(graphemes: Vec<&str>) -> Result<Node, ()> {
    let mut root_node = Node::create_node(None, Some(NodeType::Root));
    let mut i: usize = 0;
    while i < graphemes.len() {
        let mut current_node: Node = Node::create_node(None, None);
        if graphemes[i] == "<" {
            if i + 4 <= graphemes.len() && graphemes[i+1..i+4].join("").find("!--").is_some() {
                let  possible_end = graphemes[i+4..graphemes.len()].join("").find("-->");
                if let Some(end) = possible_end {
                    current_node = Node::create_comment_node(graphemes[i+4..end + 4].join(""));
                    i += 4 + 3 + end;
                }
                if possible_end.is_none() {
                    return Err(());
                }
            } else {
                if graphemes[i + 1] == "!" {
                    match find_name_end(graphemes[i+2..graphemes.len()].to_vec()) {
                        Ok(end) => {
                            current_node = Node::create_node(Some(graphemes[i+2..i+1+end].join("")), Some(NodeType::Declaration));
                            if graphemes[i+1+end] != "!" {
                                current_node.attributes = create_attribute_map(graphemes[i+2+end..graphemes.len()].to_vec());
                            }
                        }
                        Err(e) => { return Err(e); }
                    }
                } else if graphemes[i + 1] == "?" {
                    match find_name_end(graphemes[i+2..graphemes.len()].to_vec()) {
                        Ok(end) => {
                            current_node = Node::create_node(Some(graphemes[i+2..i+1+end].join("")), Some(NodeType::Processing));
                            if graphemes[i+1+end] != "?" {
                                current_node.attributes = create_attribute_map(graphemes[i+2+end..graphemes.len()].to_vec());
                            }
                        }
                        Err(e) => { return Err(e); }
                    }
                } else {
                    match find_name_end(graphemes[i+2..graphemes.len()].to_vec()) {
                        Ok(end) => {
                            current_node = Node::create_node(Some(graphemes[i+2..i+1+end].join("")), Some(NodeType::Node));
                            if graphemes[i+1+end] == " " || graphemes[i+1+end] == "\t" || graphemes[i+1+end] == "\n" {
                                current_node.attributes = create_attribute_map(graphemes[i+2+end..graphemes.len()].to_vec());
                            }
                            let possible_tag_end = graphemes[i..graphemes.len()].join("").find(">");
                            if possible_tag_end.is_none() {
                                return Err(());
                            }
                            if Node::is_unpaired(current_node.name.clone()) {
                                i += possible_tag_end.unwrap();
                            } else {
                                let end_node = format!("</{}>", current_node.name.clone());
                                let possible_closing_tag = graphemes[i..graphemes.len()].join("").find(&end_node);
                                match possible_closing_tag {
                                    Some(mut pct) => {
                                        let start_tag = format!("<{}", current_node.name);
                                        while graphemes[possible_tag_end.unwrap()..pct].join("").find(&start_tag) == graphemes[possible_tag_end.unwrap()..pct].join("").find(&end_node) {
                                            let j = graphemes[pct+1..graphemes.len()].join("").find(&end_node);
                                            if let Some(k) = j {
                                                pct += 1 + k;
                                            } else {
                                                return Err(());
                                            }
                                        }

                                        match process_nodes(graphemes[possible_tag_end.unwrap()..pct].to_vec()) {
                                            Err(e) => { return Err(e); }
                                            Ok(node)=> { current_node.children = node.children; }
                                        }
                                    }
                                    None => {
                                        return Err(());
                                    }
                                }
                            }
                        }
                        Err(e) => { return Err(e); }
                    }
                }
            }
        } else {
            let possible_end = graphemes[i..graphemes.len()].join("").find("<");
            if let Some(end) = possible_end {
                current_node = Node::create_text_node(graphemes[i..end].join(""));
                i += end;
            } else {
                current_node = Node::create_text_node(graphemes[i..graphemes.len()].join(""));
                i = graphemes.len();
            }
        }
        root_node.children.push(current_node.clone());
    }
    Ok(root_node)
}

fn find_name_end(g: Vec<&str>) -> Result<usize, ()> {
    let mut j = 0;

    while j < g.len() {
        match g[j] {
            "\n" | " " | "\t" | ">" => { return Ok(j); }
            "/" => {
                if j+1 < g.len() && g[j+1] == ">" {
                    return Ok(j);
                }
                j += 1;
            }
            _ => { j+=1; }
        }
    }
    Err(())
}

fn create_attribute_map(g: Vec<&str>) -> HashMap<String, Option<String>> {
    let mut result = HashMap::new();
    let mut j = 0;
    let mut start = 0;
    let mut key = String::new();
    let mut value = String::new();
    let mut quote: &str = "";
    while j < g.len() {
        if g[j] == "=" {
            key = g[start..j].join("");
            start = j + 2;
            quote = g[j + 1];
            let mut end = j + 3 + g[j + 3..g.len()].join("").find(quote).unwrap();
            while j < g.len() && g[g[j + 3..g.len()].join("").find(quote).unwrap()] == "\\" {
                end += g[j + 3..g.len()].join("").find(quote).unwrap() + 4;
            }
            value = g[start..end].join("");
            result.insert(key, Some(value));
            j = end + 2;
            start = j;
        } else if g[j] == " " || g[j] == "\t" || g[j] == "\n" {
            if j != start {
                result.insert(g[start..j].join(""), None);
            }
            j += 1;
            while g[j] == " " || g[j] == "\t" || g[j] == "\n" {
                j += 1;
            }
            start = j;
        } else if j + 1 == g.len() && start != j {
            result.insert(g[start..j + 1].join(""), None);
            j += 1
        } else {
            j += 1;
        }
    }
    result
}

#[cfg(test)]
mod find_name_tests {
    use super::*;

    #[test]
    fn find_name_end_space() {
        let chars: Vec<&str> = "abc ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_space_b() {
        let chars: Vec<&str> = "abc def ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_new_line() {
        let chars: Vec<&str> = "abc\ndef ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_tab() {
        let chars: Vec<&str> = "abc\tdef ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_end_mark_a() {
        let chars: Vec<&str> = "abc/> ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_end_mark_b() {
        let chars: Vec<&str> = "abc> ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }
}

#[cfg(test)]
mod attribute_tests {
    use super::*;

    #[test]
    fn create_attribute_map_key_value() {
        let chars: Vec<&str> = "abc='def'".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        assert_eq!(result.get("abc").unwrap().to_owned().unwrap(), "def");
    }

    #[test]
    fn create_attribute_map_two_key_value() {
        let chars: Vec<&str> = "abc='def' ghi='jkl'".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        println!("{:?}", result);
        assert_eq!(result.get("abc").unwrap().to_owned().unwrap(), "def");
        assert_eq!(result.get("ghi").unwrap().to_owned().unwrap(), "jkl");
    }

    #[test]
    fn create_attribute_map_key_only() {
        let chars: Vec<&str> = "abc".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        assert_eq!(result.contains_key("abc"), true);
    }

    #[test]
    fn create_attribute_map_two_keys_only() {
        let chars: Vec<&str> = "abc jkl".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        println!("{:?}", result);
        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("jkl"), true);
    }

    #[test]
    fn create_attribute_map_two_mixed_a() {
        let chars: Vec<&str> = "abc ghi='jkl'".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        println!("{:?}", result);
        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("ghi"), true);
        assert_eq!(result.get("ghi").unwrap().to_owned().unwrap(), "jkl");
    }

    #[test]
    fn create_attribute_map_two_mixed_b() {
        let chars: Vec<&str> = "ghi='jkl' abc".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        println!("{:?}", result);
        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("ghi"), true);
        assert_eq!(result.get("ghi").unwrap().to_owned().unwrap(), "jkl");
    }

    #[test]
    fn create_attribute_map_two_keys_only_double_space() {
        let chars: Vec<&str> = "abc  jkl".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        println!("{:?}", result);
        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("jkl"), true);
    }

    #[test]
    fn create_attribute_map_two_keys_only_new_line_tab() {
        let chars: Vec<&str> = "abc\n\tjkl".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);
        println!("{:?}", result);
        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("jkl"), true);
    }
}
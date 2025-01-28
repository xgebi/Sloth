use std::collections::HashMap;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use pgs_common::patterns::{Pattern, Patterns};

pub(crate) fn parse_toe(sm: String) -> Result<Node, ()> {
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
        // First clause is for opening tag, valid XML can't have these tags out of order
        if graphemes[i] == "<" {
            // check for comments
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
                // Check for Document Type Definition
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
                // Check for declarations
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
                    // Check where the name of the tag ends
                    match find_name_end(graphemes[i+1..graphemes.len()].to_vec()) {
                        Ok(end) => {
                            current_node = Node::create_node(Some(graphemes[i+1..i+end+1].join("")), Some(NodeType::Node));
                            let possible_tag_end = graphemes[i..graphemes.len()].join("").find(">");
                            if possible_tag_end.is_none() {
                                return Err(());
                            }
                            let mut tag_end = possible_tag_end.unwrap();
                                if graphemes[tag_end - 1] == "/" {
                                    tag_end -= 1;
                                }
                            if graphemes[i+1+end] == " " || graphemes[i+1+end] == "\t" || graphemes[i+1+end] == "\n" {
                                current_node.attributes = create_attribute_map(graphemes[i+2+end..tag_end].to_vec());
                            }
                            if Node::is_unpaired(current_node.name.clone()) || graphemes[tag_end] == "/"{
                                if graphemes[tag_end] == "/" {
                                    i += tag_end + 2;
                                } else {
                                    i += tag_end + 1;
                                }
                            } else {
                                let end_node = format!("</{}>", current_node.name.clone());
                                let possible_closing_tag = graphemes[i..graphemes.len()].join("").find(&end_node);
                                match possible_closing_tag {
                                    Some(mut pct) => {
                                        let start_tag = format!("<{}", current_node.name);
                                        let pte = possible_tag_end.unwrap();

                                        while graphemes[pte..pct].join("").match_indices(&start_tag).count() != graphemes[pte..pct].join("").match_indices(&end_node).count() {
                                            let j = graphemes[pct+1..graphemes.len()].join("").find(&end_node);
                                            if let Some(k) = j {
                                                pct += 1 + k;
                                            } else {
                                                return Err(());
                                            }
                                        }

                                        match process_nodes(graphemes[pte + 1..pct].to_vec()) {
                                            Err(e) => { return Err(e); }
                                            Ok(node)=> { current_node.children = node.children; }
                                        }
                                        i += pct + end_node.len();
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
    fn find_name_end_space_two_character_sequences() {
        let chars: Vec<&str> = "abc def ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_new_line_between_character_sequences() {
        let chars: Vec<&str> = "abc\ndef ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_tab_between_character_sequences() {
        let chars: Vec<&str> = "abc\tdef ".split_terminator("").skip(1).collect();
        let result = find_name_end(chars);
        assert_eq!(result.unwrap(), 3);
    }

    #[test]
    fn find_name_end_end_mark_with_slash() {
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

        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("jkl"), true);
    }

    #[test]
    fn create_attribute_map_with_boolean_and_string_value() {
        let chars: Vec<&str> = "abc ghi='jkl'".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);

        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("ghi"), true);
        assert_eq!(result.get("abc").is_some(), true);
        assert_eq!(result.get("abc").unwrap().is_none(), true);
        assert_eq!(result.get("ghi").unwrap().to_owned().unwrap(), "jkl");
    }

    #[test]
    fn create_attribute_map_with_string_and_boolean_value() {
        let chars: Vec<&str> = "ghi='jkl' abc".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);

        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("ghi"), true);
        assert_eq!(result.get("ghi").unwrap().to_owned().unwrap(), "jkl");
    }

    #[test]
    fn create_attribute_map_two_keys_only_double_space() {
        let chars: Vec<&str> = "abc  jkl".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);

        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("jkl"), true);
    }

    #[test]
    fn create_attribute_map_two_keys_only_new_line_tab() {
        let chars: Vec<&str> = "abc\n\tjkl".split_terminator("").skip(1).collect();
        let result = create_attribute_map(chars);

        assert_eq!(result.contains_key("abc"), true);
        assert_eq!(result.contains_key("jkl"), true);
    }
}

#[cfg(test)]
mod node_tests {
    use super::*;

    #[test]
    fn parse_img() {
        let chars: Vec<&str> = "<img />".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);
        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "img");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_img_unclosed() {
        let chars: Vec<&str> = "<img>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);
        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "img");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_img_unclosed_with_attribute() {
        let chars: Vec<&str> = "<img src=\"abc\">".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);
        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "img");
                assert_eq!(r.children[0].attributes.contains_key("src"), true);
                let attr = r.children[0].attributes.get("src").unwrap().to_owned().unwrap();
                assert_eq!(attr, "abc");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_img_with_attribute() {
        let chars: Vec<&str> = "<img src=\"abc\" />".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);
        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "img");
                assert_eq!(r.children[0].attributes.contains_key("src"), true);
                let attr = r.children[0].attributes.get("src").unwrap().to_owned().unwrap();
                assert_eq!(attr, "abc");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div() {
        let chars: Vec<&str> = "<div></div>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);
        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_unpaired() {
        let chars: Vec<&str> = "<div />".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                println!("{:?}", r);
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_with_content() {
        let chars: Vec<&str> = "<div>abc</div>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
                assert_eq!(r.children[0].children.len(), 1);
                assert_eq!(r.children[0].children[0].content, "abc");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_unpaired_with_key_value_attribute() {
        let chars: Vec<&str> = "<div my-attr/>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_unpaired_with_key_attribute() {
        let chars: Vec<&str> = "<div my-attr='val'/>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
                assert_eq!(r.children[0].attributes.contains_key("my-attr"), true);
                let attr = r.children[0].attributes.get("my-attr").unwrap().to_owned().unwrap();
                assert_eq!(attr, "val");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_paired_with_key_value_attribute() {
        let chars: Vec<&str> = "<div my-attr='val'></div>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
                assert_eq!(r.children[0].attributes.contains_key("my-attr"), true);
                let attr = r.children[0].attributes.get("my-attr").unwrap().to_owned().unwrap();
                assert_eq!(attr, "val");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_paired_with_two_key_value_attributes() {
        let chars: Vec<&str> = "<div my-attr='val' other='value'></div>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
                assert_eq!(r.children[0].attributes.contains_key("my-attr"), true);
                let attr = r.children[0].attributes.get("my-attr").unwrap().to_owned().unwrap();
                assert_eq!(attr, "val");

                assert_eq!(r.children[0].attributes.contains_key("other"), true);
                let attr = r.children[0].attributes.get("other").unwrap().to_owned().unwrap();
                assert_eq!(attr, "value");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_paired_with_two_key_value_attributes_and_content() {
        let chars: Vec<&str> = "<div my-attr='val' other='value'>some stuff</div>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
                assert_eq!(r.children[0].attributes.contains_key("my-attr"), true);
                let attr = r.children[0].attributes.get("my-attr").unwrap().to_owned().unwrap();
                assert_eq!(attr, "val");

                assert_eq!(r.children[0].attributes.contains_key("other"), true);
                let attr = r.children[0].attributes.get("other").unwrap().to_owned().unwrap();
                assert_eq!(attr, "value");

                assert_eq!(r.children[0].children.len(), 1);
                assert_eq!(r.children[0].children[0].content, "some stuff");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_div_paired_with_two_key_value_attributes_content_and_nested_element() {
        let chars: Vec<&str> = "<div my-attr='val' other='value'><img src='abc' /></div>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "div");
                assert_eq!(r.children[0].attributes.contains_key("my-attr"), true);
                let attr = r.children[0].attributes.get("my-attr").unwrap().to_owned().unwrap();
                assert_eq!(attr, "val");

                assert_eq!(r.children[0].attributes.contains_key("other"), true);
                let attr = r.children[0].attributes.get("other").unwrap().to_owned().unwrap();
                assert_eq!(attr, "value");

                assert_eq!(r.children[0].children.len(), 1);
                assert_eq!(r.children[0].children[0].name, "img");
                assert_eq!(r.children[0].children[0].attributes.contains_key("src"), true);
                let attr = r.children[0].children[0].attributes.get("src").unwrap().to_owned().unwrap();
                assert_eq!(attr, "abc");
            }
            Err(_) => { panic!(); }
        }
    }

    #[test]
    fn parse_custom_element_unpaired_with_two_key_value_attributes_content_and_nested_custom_element() {
        let chars: Vec<&str> = "<my-element my-attr='val' other='value'><h1- src='abc' /></my-element>".split_terminator("").skip(1).collect();
        let result = process_nodes(chars);

        match result {
            Ok(r) => {
                assert_eq!(r.children.len(), 1);
                assert_eq!(r.children[0].name, "my-element");
                assert_eq!(r.children[0].attributes.contains_key("my-attr"), true);
                let attr = r.children[0].attributes.get("my-attr").unwrap().to_owned().unwrap();
                assert_eq!(attr, "val");

                assert_eq!(r.children[0].attributes.contains_key("other"), true);
                let attr = r.children[0].attributes.get("other").unwrap().to_owned().unwrap();
                assert_eq!(attr, "value");

                assert_eq!(r.children[0].children.len(), 1);
                assert_eq!(r.children[0].children[0].name, "h1-");
                assert_eq!(r.children[0].children[0].attributes.contains_key("src"), true);
                let attr = r.children[0].children[0].attributes.get("src").unwrap().to_owned().unwrap();
                assert_eq!(attr, "abc");
            }
            Err(_) => { panic!(); }
        }
    }
}
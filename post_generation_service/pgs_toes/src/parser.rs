use std::collections::HashMap;
use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use pgs_common::patterns::Patterns;

fn parse_toe(sm: String) -> Result<Node, Err()> {
    let patterns = Patterns::new();
    let processed_new_lines = sm.replace(
        patterns.locate("double_line_win").unwrap().value.as_str(),
        patterns.locate("double_line").unwrap().value.as_str()
    );
    let grapheme_vector = processed_new_lines.graphemes(true).collect::<Vec<&str>>();
    process_nodes(grapheme_vector)
}

fn process_nodes(graphemes: Vec<&str>) -> Result<Node, Err()> {
    let mut root_node = Node::create_node(None, Some(NodeType::Root));
    let mut i: usize = 0;
    while i < graphemes.len() {
        let mut current_node: Node = Node::create_node(None, None);
        if graphemes[i] == "<" {
            if i + 4 <= graphemes.len() && graphemes[i+1..i+4].join("").find("!--").is_some() {
                let  possible_end = graphemes[i+4..graphemes.len()].join("").find("-->");
                if let (end) = possible_end {
                    current_node = Node::create_comment_node(graphemes[i+4..end + 4].join(""));
                    i += 4 + 3 + end;
                }
                if possible_end.is_none() {
                    return Err(());
                }
            } else {
                if graphemes[i + 1] == "!" {
                    match find_name_end(g[i+2..graphemes.len()]) {
                        Some(end) => {
                            current_node = Node::create_node(Some(g[i+2..i+1+end]), Some(NodeType::Declaration));
                            if g[i+1+end] != "!" {
                                current_node.attributes = create_attribute_map(graphemes[i+2+end..graphemes.len()]);
                            }
                        }
                        Err(e) => { return e; }
                    }
                } else if graphemes[i + 1] == "?" {
                    match find_name_end(g[i+2..graphemes.len()]) {
                        Some(end) => {
                            current_node = Node::create_node(Some(g[i+2..i+1+end]), Some(NodeType::Processing));
                            if g[i+1+end] != "?" {
                                current_node.attributes = create_attribute_map(graphemes[i+2+end..graphemes.len()]);
                            }
                        }
                        Err(e) => { return e; }
                    }
                } else {
                    match find_name_end(g[i+2..graphemes.len()]) {
                        Some(end) => {
                            current_node = Node::create_node(Some(g[i+2..i+1+end]), Some(NodeType::Node));
                            if g[i+1+end] == " " || g[i+1+end] == "\t" || g[i+1+end] == "\n" {
                                current_node.attributes = create_attribute_map(graphemes[i+2+end..graphemes.len()]);
                            }
                            let possible_tag_end = graphemes[i..graphemes.len()].join("").find(">");
                            if possible_tag_end.is_none() {
                                return Err(());
                            }
                            if Node::is_unpaired(current_node.name) {
                                i += possible_tag_end.unwrap();
                            } else {
                                let possible_closing_tag = graphemes[i..graphemes.len()].join("").find(format!("</{}>", current_node.name));
                                match possible_closing_tag {
                                    Some(mut pct) => {
                                        while graphemes[possible_tag_end.unwrap()..pct].join("").find(format!("<{}", current_node.name)) == graphemes[possible_tag_end.unwrap()..pct].join("").find(format!("</{}>", current_node.name)) {
                                            let j = graphemes[pct+1..graphemes.len()].join("").find(format!("</{}>", current_node.name));
                                            pct += 1 + j;
                                        }

                                        // get child nodes
                                    }
                                    None => {
                                        return Err(());
                                    }
                                }
                            }
                        }
                        Err(e) => { return e; }
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
        root_node.children.push(current_node.unwrap());
    }
    Ok(root_node)
}

fn find_name_end(g: Vec<&str>) -> Result<usize, Err()> {
    let mut j = 0;

    while j < g.len() {
        match g[j] {
            "\n" | " " | "\t" | ">" | "/>" => { return Ok(j); }
            _ => { j+=1; }
        }
    }
    Err(())
}

fn create_attribute_map(graphemes: Vec<&str>) -> HashMap<String, String> {
    let mut result = HashMap::new();

    result
}
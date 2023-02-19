use unicode_segmentation::UnicodeSegmentation;
use pgs_common::node::{Node, NodeType};
use pgs_common::patterns::Patterns;

fn parse_toe(sm: String) -> Node {
    let patterns = Patterns::new();
    let processed_new_lines = sm.replace(
        patterns.locate("double_line_win").unwrap().value.as_str(),
        patterns.locate("double_line").unwrap().value.as_str()
    );
    let grapheme_vector = processed_new_lines.graphemes(true).collect::<Vec<&str>>();
    process_nodes(grapheme_vector)
}

fn process_nodes(graphemes: Vec<&str>) -> Node {
    let mut root_node = Node::create_node(None, Some(NodeType::Root));
    let mut current_node: &mut Node = &mut root_node;
    let mut i: usize = 0;
    while i < graphemes.len() {
        if graphemes[i] == "<" {
            let mut j = i + 1;
            while j < graphemes.len() {
                match graphemes[j] {
                    "\n" | " " | "\t" | ">" | "/>" => { break; }
                    _ => { j+=1; }
                }
            }
            root_node.name = graphemes[i..j].join("");


        }
    }
    root_node
}

fn get_minimum<'a>(v: Vec<Option<usize>>) -> Option<usize> {
    let mut temp = Vec::new();

    for i in v {
        if let Some(unwrapped) = i {
            temp.push(unwrapped.clone());
        }
    }

    temp.iter().min().cloned()
}
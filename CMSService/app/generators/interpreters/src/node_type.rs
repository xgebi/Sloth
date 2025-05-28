#[derive(Debug, Clone, PartialEq)]
pub enum NodeType {
    Text,
    Normal,
    Processing,
    DocumentTypeDefinition,
    Comment,
    CDATA,
    ToeRoot // Special type of node 
}
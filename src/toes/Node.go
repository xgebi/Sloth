package toes

type NodeTypes string

const (
	Node           NodeTypes = "node"
	RootNode                 = "root"
	ProcessingNode           = "processing"
	DirectiveNode            = "directive"
	TextNode                 = "text"
	CommentNode              = "comment"
	CdataTextNode            = "cdata"
)

package toes

type NodeTypes string

const (
	NormalNode     NodeTypes = "node"
	RootNode                 = "root"
	ProcessingNode           = "processing"
	DirectiveNode            = "directive"
	TextNode                 = "text"
	CommentNode              = "comment"
	CdataTextNode            = "cdata"
)

type Node struct {
	name       string
	attributes map[string]string
	pairedTag  bool
	parent     *Node
	children   []*Node
	cdata      bool
	content    string
	doctype    string
	html       bool
}

// Root Node

func (node *Node) NewRootNode() Node {
	return Node{}
}

// Standard Node

func (node *Node) NewNode() Node {
	return Node{}
}

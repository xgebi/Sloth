package toes

import "errors"

type States int

const (
	NewPage States = iota
	ReadNodeName
	LookingForAttribute
	LookingForChildNodes
	InsideScript
)

type XmlParsingInfo struct {
	index       int
	state       States
	currentNode *Node
	rootNode    *Node
}

func (xpi *XmlParsingInfo) MoveIndex(step ...int) {
	switch len(step) {
	case 0:
		xpi.index += 1
	case 1:
		xpi.index += step[0]
	default:
		errors.New("parsing error: cannot move index with more than one step value")
	}
}

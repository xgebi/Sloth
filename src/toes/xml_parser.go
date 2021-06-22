package toes

type States int

const (
	NewPage States = iota
	ReadNodeName
	LookingForAttribute
	LookingForChildNodes
	InsideScript
)

type XmlParsingInfo struct {
	index int
	state States
}

//type rect struct {
//    width, height int
//}
//
//This area method has a receiver type of *rect.
//
//
//func (r *rect) area() int {
//    return r.width * r.height
//}

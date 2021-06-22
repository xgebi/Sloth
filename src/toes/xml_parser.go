package toes

import (
	"io/ioutil"
	"path/filepath"
)

type XmlParser struct {
	text string
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func (xp *XmlParser) NewParserFromPath(basePath string, path string) XmlParser {
	template, err := ioutil.ReadFile(filepath.Join(basePath, path))
	check(err)

	return XmlParser{text: string(template)}
}

func (xp *XmlParser) NewParserFromTemplate(template string) XmlParser {
	return XmlParser{text: template}
}

func (xp *XmlParser) ParseFile() Node {
	return Node{}
}

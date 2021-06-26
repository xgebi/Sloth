package main

import "C"

type PostGeneratorData struct {
	runnable  bool
	themePath string
}

//export PostGenerator
func PostGenerator() {

}

func main() {}

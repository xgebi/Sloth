package main

import (
	"C"

	"github.com/xgebi/Sloth/toes"
)

type PostGeneratorData struct {
	runnable  bool
	themePath string
}

//export RegenerateAll
func RegenerateAll(db_url string,
	db_port int,
	db_user string,
	db_pass string,
	db_name string,
	output string) {

}

//export GeneratePost
func GeneratePost(
	post_uuid string,
	db_url string,
	db_port int,
	db_user string,
	db_pass string,
	db_name string,
	output string) {
	toes.get_settings()
}

//export GeneratePostType
func GeneratePostType(
	post_type_uuid string,
	db_url string,
	db_port int,
	db_user string,
	db_pass string,
	db_name string,
	output string) {
	toes.get_settings()
}

//export RegenerateTaxonomy
func RegenerateTaxonomy(
	post_type_uuid string,
	lang string,
	db_url string,
	db_port int,
	db_user string,
	db_pass string,
	db_name string,
	output string) {
	toes.get_settings()
}

func main() {}

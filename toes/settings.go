package toes

type Settings struct {
}

//DATABASE_URL = 'localhost'
//DATABASE_PORT = 5432
//DATABASE_USER = 'sloth'
//DATABASE_PASSWORD = 'sloth'
//DATABASE_NAME = 'sloth'
//OUTPUT_PATH = 'site'

func get_settings(
	db_url string,
	db_port int,
	db_user string,
	db_pass string,
	db_name string,
	output string) Settings {
	return Settings{}
}

use postgres::{Client, Error, NoTls, Row};
use dotenv::dotenv;
use std::env;
use crate::models::single_post::SinglePost;

fn connect() -> Result<Client, Error> {
    dotenv().ok();
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    Client::connect("host=localhost user=postgres", NoTls)
}

pub fn get_single_post() -> Option<&Row> {
    let mut db = connect()?;

    let result = db.query("SELECT id, name, data FROM person", &[]);
    match result {
        Ok(res) => {
            if !res.is_empty() {
                return res.get(0);
            }
            None
        },
        Err(_) => None
    }
}

pub fn get_archive(post_type: String) -> Option<Vec<SinglePost>> {
    let mut db = connect()?;
    let raw_result = db.query("SELECT id, name, data FROM person", &[]);
    match raw_result {
        Ok(res) => {
            if !res.is_empty() {
                let mut result = Vec::new();
                for row in res {
                    result.push(row_to_single_post(row))
                }
                return Some(result);
            }
            None
        },
        Err(_) => None
    }
}

pub fn get_taxonomy_archive(post_type: String, taxonomy: String) -> Option<Vec<SinglePost>> {
    let mut db = connect()?;
    let raw_result = db.query("SELECT id, name, data FROM person", &[]);
    match raw_result {
        Ok(res) => {
            if !res.is_empty() {
                let mut result = Vec::new();
                for row in res {
                    result.push(row_to_single_post(row))
                }
                return Some(result);
            }
            None
        },
        Err(_) => None
    }
}

fn row_to_single_post(row: Row) -> SinglePost {
    SinglePost {
        title: String::new()
    }
}
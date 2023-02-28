use postgres::{Client, NoTls, Row};
use std::env;
use std::error::Error;
use crate::models::post_status::PostStatus;
use crate::models::single_post::SinglePost;

fn connect() -> Result<Client, ()> {
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let client = Client::connect("host=localhost user=postgres", NoTls);
    match client {
        Ok(c) => { return Ok(c); }
        Err(_) => {return Err(()); }
    }
}

pub fn get_single_post(uuid: String) -> Option<SinglePost> {
    let mut db_result = connect();
    if let Ok(db) = db_result {
        let _stmt = format!("{}{}", include_str!("queries/post/post.sql"), include_str!("queries/post/single_post.sql"));
        let result = db.query(_stmt, &[uuid]);
        if let Ok(res) = result {
            if !res.is_empty() {
                for row in res {
                    return Some(row_to_single_post(row));
                }
            }
        }
    }
    None
}

pub fn get_archive(post_type: String) -> Option<Vec<SinglePost>> {
    let mut db_result = connect();
    if let Ok(db) = db_result {
        let _stmt = format!("{}{}", include_str!("queries/post/post.sql"), include_str!("queries/post/post_type_archive.sql"));
        let result = db.query(_stmt, &[post_type]);
        if let Ok(res) = result {
            if !res.is_empty() {
                let mut result = Vec::new();
                for row in res {
                    result.push(row_to_single_post(row))
                }
                return Some(result);
            }
        }
    }
    None
}

pub fn get_taxonomy_archive(post_type: String, taxonomy: String) -> Option<Vec<SinglePost>> {
    let mut db_result = connect();
    if let Ok(db) = db_result {
        let _stmt = include_str!("different file");
        let result = db.query(_stmt, &[]);
        if let Ok(res) = result {
            if !res.is_empty() {
                let mut result = Vec::new();
                for row in res {
                    result.push(row_to_single_post(row))
                }
                return Some(result);
            }
        }
    }
    None
}

fn row_to_single_post(row: Row) -> SinglePost {
    SinglePost {
        title: String::new(),
        uuid: "".to_string(),
        original_lang_entry_uuid: "".to_string(),
        lang: "".to_string(),
        slug: "".to_string(),
        post_type: "".to_string(),
        author: "".to_string(),
        content: "".to_string(),
        excerpt: "".to_string(),
        css: "".to_string(),
        use_theme_css: false,
        js: "".to_string(),
        use_theme_js: false,
        thumbnail: "".to_string(),
        publish_date: 0.0,
        update_date: 0.0,
        post_status: PostStatus::Published,
        post_format: "".to_string(),
        imported: false,
        import_approved: false,
        password: "".to_string(),
        meta_description: "".to_string(),
        twitter_description: "".to_string(),
        pinned: false,
    }
}
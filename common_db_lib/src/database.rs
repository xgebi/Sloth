// use postgres::{Client, NoTls, Row};
use tokio_postgres::{NoTls, Client, Row, Socket, Connection};
use std::env;
use std::error::Error;
use sloth_config_lib::{get_config, SlothConfig};
use tokio_postgres::tls::NoTlsStream;
use crate::models::post_status::PostStatus;
use crate::models::single_post::SinglePost;


pub async fn connect(conf: Option<SlothConfig>) -> Result<Client, ()> {
    let config: SlothConfig = match conf {
        Some(c) => { c }
        None => {
            if let Ok(c) = get_config() {
                c
            } else {
                panic!()
            }
        }
    };

    let conn_result =
        tokio_postgres::connect("host=localhost user=postgres", NoTls).await;
    match conn_result {
        Ok((client, connection)) => {
            if let Err(e) = connection.await {
                eprintln!("connection error: {}", e);
                return Err(());
            }
            Ok(client)
        }
        Err(_) => { return Err(())}
    }
}

pub async fn get_single_post(uuid: String) -> Option<SinglePost> {
    let mut db_result = connect(None).await;
    if let Ok(mut db) = db_result {
        let _stmt = format!("{}{}", include_str!("queries/post/post.sql"), include_str!("queries/post/single_post.sql"));
        let result = db.query_one(&_stmt, &[&uuid]).await;
        if let Ok(res) = result {
            return Some(row_to_single_post(res));
        }
    }
    None
}

pub async fn get_archive(post_type: String) -> Option<Vec<SinglePost>> {
    let mut db_result = connect(None).await;
    if let Ok(mut db) = db_result {
        let _stmt = format!("{}{}", include_str!("queries/post/post.sql"), include_str!("queries/post/post_type_archive.sql"));
        let result = db.query(&_stmt, &[&post_type]).await;
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

pub async fn get_taxonomy_archive(post_type: String, taxonomy: String) -> Option<Vec<SinglePost>> {
    let mut db_result = connect(None).await;
    if let Ok(mut db) = db_result {
        let _stmt = format!("{}{}", include_str!("queries/post/post.sql"), include_str!("queries/post/taxonomy_archive.sql"));
        let result = db.query(&_stmt, &[&taxonomy, &post_type]).await;
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
use std::time::{SystemTime, UNIX_EPOCH};
use postgres::Client;
use uuid::{uuid, Uuid};
use common_db_lib::database::connect;

pub(crate) fn remove_token(user_id: String, token: String) -> bool {
    let mut db_result = connect();
    if let Ok(mut db) = db_result {
        let _stmt = include_str!("queries/remove_token.sql");
        let result = db.execute(_stmt, &[&user_id, &token]);
        return result.is_ok();
    }
    false
}

pub(crate) fn create_token(user_id: String) -> Option<(String, i64)> {
    let mut db_result = connect();
    if let Ok(mut db) = db_result {
        let _stmt = include_str!("queries/create_token.sql");
        let id = Uuid::new_v4().to_string();
        let token = Uuid::new_v4().to_string();
        let expiration = (SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards")
            .as_millis() + (30 * 60 * 1000)) as i64;
        let result = db.execute(_stmt, &[&id, &user_id, &token, &expiration]);
        if result.is_ok() {
            return Some((token.clone(), expiration));
        }
    }
    None
}

pub(crate) fn refresh_token(user_id: String, token: String) -> bool {
    let mut db_result = connect();
    if let Ok(mut db) = db_result {
        if !is_token_valid(user_id.clone(), token.clone(), &mut db) {
            return false;
        }
        let _stmt = include_str!("queries/create_token.sql");
        let expiration = (SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards")
            .as_millis() + (30 * 60 * 1000)) as i64;
        let result = db.execute(_stmt, &[&expiration, &(user_id.clone()), &(token.clone())]);
        return result.is_ok();
    }
    false
}

pub(crate) fn is_token_valid(user_id: String, token: String, mut client: &mut Client) -> bool {
    let _stmt = include_str!("queries/check_token.sql");
    let result = client.query_one(_stmt, &[&user_id, &token]);
    return result.is_ok();
}

pub(crate) fn can_access(user_id: String, role: String) -> bool {
    todo!();
}
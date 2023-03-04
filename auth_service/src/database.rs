use common_db_lib::database::connect;

pub(crate) fn fetch_hash(uuid: String) -> Option<(String, String)> {
    let mut db_result = connect();
    if let Ok(mut db) = db_result {
        let _stmt = include_str!("queries/get_password.sql");
        let result = db.query_one(_stmt, &[&uuid]);
        if let Ok(res) = result {
            let algo: String = res.get(0);
            let password: String = res.get(1);
            return Some((algo, password));
        }
    }
    None
}

pub(crate) fn update_hash(alg:String, hash: String, uuid: String) -> bool {
    let mut db_result = connect();
    if let Ok(mut db) = db_result {
        let _stmt = include_str!("queries/update_password.sql");
        let result = db.execute(_stmt, &[&alg, &hash, &uuid]);
        return result.is_ok();
    }
    false
}

pub(crate) fn create_hash(alg:String, hash: String, uuid: String) -> bool {
    let mut db_result = connect();
    if let Ok(mut db) = db_result {
        let _stmt = include_str!("queries/create_password.sql");
        let result = db.execute(_stmt, &[&uuid, &hash, &alg]);
        return result.is_ok();
    }
    false
}
use pwhash::bcrypt;
use crate::authentication::argon::rehash_password;

pub(crate) fn verify_password(password: String, password_hash: String, uuid: String) -> (String, u64) {
    if bcrypt::verify(password.clone(), password_hash.as_str()) {
        if rehash_password(password, uuid) {
            // figure out tokens and expiration
            todo!();
        }
    }
    (String::new(), 0)
}
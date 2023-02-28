use pwhash::bcrypt;
use crate::authentication::argon::rehash_password;

pub(crate) fn verify_password(password: String, password_hash: String, uuid: String) -> bool {
    if bcrypt::verify(password.clone(), password_hash.as_str()) {
        return rehash_password(password, uuid);
    }
    false
}
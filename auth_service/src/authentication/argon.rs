use orion::pwhash;
use orion::pwhash::PasswordHash;

pub(crate) fn verify_password(password: String, password_hash: String) -> (String, u64) {
    let encoded = PasswordHash::from_encoded(&password_hash);
    if let Ok(encoded_hash) = encoded {
        let pass = pwhash::Password::from_slice(password.as_ref())?;
        if pwhash::hash_password_verify(&encoded_hash, &pass).is_ok() {
            // figure out tokens and expiration
            todo!();
        }
    }
    return (String::new(), 0)
}

pub(crate) fn rehash_password(password: String, uuid: String) -> bool {
    let pass = pwhash::Password::from_slice(password.as_ref())?;
    let hash = pwhash::hash_password(&pass, 3, 1<<16)?;
    hash.unprotected_as_encoded();
    false
}
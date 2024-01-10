use orion::pwhash;
use orion::pwhash::PasswordHash;
use crate::authorization::create_token;
use crate::database::create_hash;

pub(crate) fn verify_password(password: String, password_hash: String, uuid: String) -> bool {
    let encoded = PasswordHash::from_encoded(&password_hash);
    if let Ok(encoded_hash) = encoded {
        let pass_slice = pwhash::Password::from_slice(password.as_ref());
        if let Ok(pass) = pass_slice {
            return pwhash::hash_password_verify(&encoded_hash, &pass).is_ok();
        }
    }
    false
}

pub(crate) fn rehash_password(password: String, uuid: String) -> bool {
    if let Ok(pass) = pwhash::Password::from_slice(password.as_ref()) {
        // debug the number of iterations later
        if let Ok(hash) = pwhash::hash_password(&pass, 15, 1 << 16) {
            let hashed_password = hash.unprotected_as_encoded().to_string();
            return create_hash("argon".parse().unwrap(), hashed_password, uuid);
        }
    }
    false
}
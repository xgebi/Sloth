pub fn generate_post(
    id: String
) -> bool {
    // get post data
    generate_single_post();


    true
}

pub fn regenerate_all() -> bool {
    todo!()
}

pub fn is_generating() -> bool {
    let generating_lock = std::path::Path::new("generating.lock");
    generating_lock.exists()
}

fn generate_single_post() {

}

fn generate_archive() {

}
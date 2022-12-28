#[derive(Debug, Default)]
pub struct Generator {}

impl Generator {
    pub fn generate_post(
        id: String
    ) -> bool {
        println!("Got a id: {:?}", id);
        true
    }

    pub fn regenerate_all() -> bool {
        todo!()
    }

    pub fn regenerate_assets() -> bool {
        todo!()
    }

    pub fn is_generating() -> bool {
        let generating_lock = std::path::Path::new("generating.lock");
        generating_lock.exists()
    }
}
use std::collections::HashMap;

pub struct Settings {
    active_theme: String,
    main_language: String,
    number_rss_posts: i32,
    site_url: String,
    api_url: String,
    translatable_items: Vec<TranslatableItem>,
}

struct TranslatableItem {
    name: String,
    values: HashMap<String, String>
}
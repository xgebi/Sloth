use pyo3::types::PyDict;

pub(crate) struct Post {
    uuid: String,
    slug: String,
    display_name: String,
    author_uuid: String,
    title: String,
    css: String,
    js: String,
    use_theme_css: bool,
    use_theme_js: bool,
    publish_date: u32,
    update_date: u32,
    post_status: String,
    imported: bool,
    import_approved: bool,
    thumbnail: String,
    original_lang_entry_uuid: String,
    lang: String,
    post_format_uuid: String,
    post_format_slug: String,
    post_format_display_name: String,
    meta_description: String,
    twitter_description: String,
}

impl Post {
    pub(crate) fn new(data: &PyDict) -> Self {
        // data.get_item("slug").unwrap_or_else("").to_string()
        Post {
            uuid: data.get_item("uuid").unwrap().to_string(),
            slug: data.get_item("slug").unwrap().to_string(),
            display_name: data.get_item("slug").unwrap_or_else("").to_string(), //
            author_uuid: data.get_item("author").unwrap().to_string(),
            title: "".to_string(),
            css: "".to_string(),
            js: "".to_string(),
            use_theme_css: false,
            use_theme_js: false,
            publish_date: 0,
            update_date: 0,
            post_status: "".to_string(),
            imported: false,
            import_approved: false,
            thumbnail: "".to_string(),
            original_lang_entry_uuid: "".to_string(),
            lang: "".to_string(),
            post_format_uuid: "".to_string(),
            post_format_slug: "".to_string(),
            post_format_display_name: "".to_string(),
            meta_description: "".to_string(),
            twitter_description: "".to_string()
        }
    }
}
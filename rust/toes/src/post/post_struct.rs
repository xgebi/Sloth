use pyo3::PyAny;
use pyo3::types::PyDict;

#[derive(Default, Debug)]
struct PostSection {
    content: String,
    original: String,
    section_type: String,
    position: u16,
}

#[derive(Default, Debug)]
pub(crate) struct Post {
    uuid: String,
    slug: String,
    author_display_name: String,
    author_uuid: String,
    title: String,
    css: String,
    js: String,
    use_theme_css: bool,
    use_theme_js: bool,
    publish_date: u32,
    update_date: u32,
    publish_date_formatted: String,
    update_date_formatted: String,
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
    sections: Vec<PostSection>,
    pinned: bool,
    password: String
}

impl Post {
    pub(crate) fn new(data: &PyDict) -> Self {
        Post {
            uuid: data.get_item("uuid").unwrap().to_string(),
            slug: data.get_item("slug").unwrap().to_string(),
            author_display_name: match data.get_item("author_display_name") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            author_uuid: data.get_item("author").unwrap().to_string(),
            title: data.get_item("title").unwrap_or_else("").to_string(),
            css: data.get_item("css").unwrap_or_else("").to_string(),
            js: data.get_item("js").unwrap_or_else("").to_string(),
            use_theme_css: data.get_item("use_theme_css").unwrap_or_else(false) as bool,
            use_theme_js: data.get_item("use_theme_js").unwrap_or_else(false) as bool,
            publish_date: data.get_item("publish_date").unwrap_or_else(0) as u32,
            update_date: data.get_item("update_date").unwrap_or_else(0) as u32,
            publish_date_formatted: data.get_item("publish_date_formatted").unwrap_or_else("").to_string(),
            update_date_formatted: data.get_item("update_date_formatted").unwrap_or_else("").to_string(),
            post_status: data.get_item("post_status").unwrap().to_string(),
            imported: data.get_item("imported").unwrap_or_else(false) as bool,
            import_approved: data.get_item("import_approved").unwrap_or_else(false) as bool,
            thumbnail: data.get_item("thumbnail").unwrap_or_else("").to_string(),
            original_lang_entry_uuid: data.get_item("original_lang_entry_uuid").unwrap_or_else("").to_string(),
            lang: data.get_item("lang").unwrap().to_string(),
            post_format_uuid:  data.get_item("post_format_uuid").unwrap().to_string(),
            post_format_slug:  data.get_item("post_format_slug").unwrap().to_string(),
            post_format_display_name:  data.get_item("post_format_display_name").unwrap().to_string(),
            meta_description: data.get_item("meta_description").unwrap_or_else("").to_string(),
            twitter_description: data.get_item("twitter_description").unwrap_or_else("").to_string(),
            sections: data.get_item("twitter_description").unwrap_or_else(Vec::new()) as Vec<PostSection>,
            pinned: data.get_item("pinned").unwrap_or_else(false) as bool,
            password: data.get_item("password").unwrap_or_else("").to_string()
        }
    }


}

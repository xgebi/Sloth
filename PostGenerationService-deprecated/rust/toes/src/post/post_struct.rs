use pyo3::{IntoPy, PyAny, PyDowncastError};
use pyo3::callback::IntoPyCallbackOutput;
use pyo3::types::{PyBool, PyDict, PyFloat, PyList};

#[derive(Debug)]
struct PostSection<'a> {
    content: &'a String,
    original: &'a String,
    section_type: &'a String,
    position: u16,
}

#[derive(Debug)]
pub(crate) struct Post<'a> {
    uuid: String,
    slug: String,
    author_display_name: String,
    author_uuid: String,
    title: String,
    css: String,
    js: String,
    use_theme_css: bool,
    use_theme_js: bool,
    publish_date: f64,
    update_date: f64,
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
    sections: Vec<PostSection<'a>>,
    pinned: bool,
    password: String
}

impl<'a> Post<'a> {
    pub(crate) fn new(data: &'a PyDict) -> Self {
        Post {
            uuid: data.get_item("uuid").unwrap().to_string(),
            slug: data.get_item("slug").unwrap().to_string(),
            author_display_name: match data.get_item("author_display_name") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            author_uuid: data.get_item("author").unwrap().to_string(),
            title: match data.get_item("title") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            css: match data.get_item("css") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            js: match data.get_item("js") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            use_theme_css: match data.get_item("use_theme_css") {
                None => { true }
                Some(a) => {
                    match a.downcast::<PyBool>() {
                        Ok(temp) => { temp.is_true() }
                        Err(_) => { true }
                    }
                }
            },
            use_theme_js: match data.get_item("use_theme_js") {
                None => { true }
                Some(a) => {
                    match a.downcast::<PyBool>() {
                        Ok(temp) => { temp.is_true() }
                        Err(_) => { true }
                    }
                }
            },
            publish_date: match data.get_item("publish_date") {
                None => { 0.0 }
                Some(a) => {
                    if let Ok(res) = a.extract::<f64>() {
                        res
                    } else {
                        0.0
                    }
                }
            },
            update_date: match data.get_item("update_date") {
                None => { 0.0 }
                Some(a) => {
                    if let Ok(res) = a.extract::<f64>() {
                        res
                    } else {
                        0.0
                    }
                }
            },
            publish_date_formatted: match data.get_item("publish_date_formatted") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            update_date_formatted: match data.get_item("update_date_formatted") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            post_status: data.get_item("post_status").unwrap().to_string(),
            imported: match data.get_item("imported") {
                None => { false }
                Some(a) => {
                    match a.downcast::<PyBool>() {
                        Ok(temp) => { temp.is_true() }
                        Err(_) => { true }
                    }
                }
            },
            import_approved: match data.get_item("import_approved") {
                None => { false }
                Some(a) => {
                    match a.downcast::<PyBool>() {
                        Ok(temp) => { temp.is_true() }
                        Err(_) => { true }
                    }
                }
            },
            thumbnail: match data.get_item("thumbnail"){
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            original_lang_entry_uuid: match data.get_item("original_lang_entry_uuid") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            lang: data.get_item("lang").unwrap().to_string(),
            post_format_uuid:  data.get_item("post_format_uuid").unwrap().to_string(),
            post_format_slug:  data.get_item("post_format_slug").unwrap().to_string(),
            post_format_display_name:  match data.get_item("post_format_display_name") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            meta_description: match data.get_item("meta_description") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            twitter_description: match data.get_item("twitter_description") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            },
            sections: match data.get_item("sections") {
                None => { Vec::new() as Vec<PostSection> }
                Some(a) => {
                    // PyList
                    if let Ok(b) = a.downcast::<PyList>() {
                        for item in b.into_iter() {

                        }
                    }
                    Vec::new() as Vec<PostSection>
                }
            },
            pinned: match data.get_item("pinned") {
                None => { false }
                Some(a) => {
                    match a.downcast::<PyBool>() {
                        Ok(temp) => { temp.is_true() }
                        Err(_) => { true }
                    }
                }
            },
            password: match data.get_item("password") {
                None => { "".to_string() }
                Some(a) => { a.to_string() }
            }
        }
    }


}

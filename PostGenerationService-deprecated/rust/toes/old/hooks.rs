use std::collections::HashMap;

struct Hooks {
    pub(crate) footer: HashMap<String, String>,
    pub(crate) head: HashMap<String, String>
}

enum HooksList {
    footer,
    head
}
pub(crate) struct Hook {
    pub(crate) content: String,
    pub(crate) condition: String
}

pub(crate) struct Hooks {
    pub(crate) head: Vec<Hook>,
    pub(crate) footer: Vec<Hook>
}
use std::collections::HashMap;

// This will be probably deleted, I need it as a stepping stone to better solution
pub(crate) struct ForIteratorWrapper {
    pub(crate) vector: Option<Vec<String>>,
    pub(crate) map: Option<Vec<HashMap<String, String>>>
}
use postgres::Client;
use std::collections::HashMap;

struct Setting {
    name: str,
    value: str,
    value_type: str,
}

struct TranslatableSetting {
    setting: HashMap<str, Setting>
}

pub(crate) fn prepare_single_post(conn: Client, uuid: String, theme_path: String, output_path: String) {

}

fn prepare_settings() -> HashMap<str, Setting> {
    HashMap::new()
}

fn prepare_translatable_settings() -> HashMap<str, TranslatableSetting> {
    HashMap::new()
}
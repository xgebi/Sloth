use std::collections::HashMap;
use postgres::Row;
use postgres_types::{ToSql, FromSql};

#[derive(Default, Debug)]
pub(crate) struct Setting {
    name: String,
    value: String,
    value_type: SlothSettingsType,
}

#[derive(Default, Debug)]
pub(crate) struct TranslatableSettingItem {
    name: String,
    content: String,
    lang: String
}

#[derive(Default, Debug)]
pub(crate) struct TranslatableSetting {
    setting: HashMap<String, TranslatableSettingItem>
}

#[derive(Default, Debug)]
pub(crate) struct Menu<'a> {
    pub(crate) name: &'a String,
    pub(crate) uuid: &'a String,
    pub(crate) items: Vec<MenuItem>
}

impl<'a> Menu<'a> {
    pub(crate) fn new(name: &'a String, uuid: &'a String) -> Self {
        Self {
            name,
            uuid,
            items: Vec::new()
        }
    }

    pub(crate) fn set_item(self, items: Vec<Row>) {
        for item in items {

        }
    }
}

#[derive(Default, Debug)]
struct MenuItem {
    title: String,
    url: String
}

impl MenuItem {
    pub(crate) fn new(title: String, url: String) -> Self {
        Self {
            title,
            url
        }
    }
}

#[derive(Debug, ToSql, FromSql)]
#[postgres(name = "sloth_settings_type")]
enum SlothSettingsType {
    #[postgres(name = "boolean")]
    Boolean,
    #[postgres(name = "text")]
    Text,
    #[postgres(name = "text-long")]
    TextLong,
    #[postgres(name = "select")]
    Select
}
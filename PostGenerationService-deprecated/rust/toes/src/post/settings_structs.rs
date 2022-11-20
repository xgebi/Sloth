use std::collections::HashMap;
use postgres::Row;
use postgres_types::{ToSql, FromSql};

#[derive(Debug)]
pub(crate) struct Setting {
    name: String,
    value: String,
    value_type: SlothSettingsType,
}

#[derive(Debug)]
pub(crate) struct TranslatableSettingItem {
    name: String,
    content: String,
    lang: String
}

#[derive(Debug)]
pub(crate) struct TranslatableSetting {
    setting: HashMap<String, TranslatableSettingItem>
}

#[derive(Debug)]
pub(crate) struct Menu {
    pub(crate) name: String,
    pub(crate) uuid: String,
    pub(crate) items: Vec<MenuItem>
}

impl Menu {
    pub(crate) fn new(name: String, uuid: String) -> Menu {
        Menu {
            name,
            uuid,
            items: Vec::new()
        }
    }

    pub(crate) fn set_item(self, items: &Vec<Row>) {
        for item in items {

        }
    }
}

#[derive(Default, Debug)]
pub(crate) struct MenuItem {
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
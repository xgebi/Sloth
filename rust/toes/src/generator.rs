use postgres::{Client, Row};
use std::collections::HashMap;
use std::error::Error;
use std::string::String;
use std::sync::Arc;
use pyo3::types::PyDict;
use postgres_types::{ToSql, FromSql};
use std::collections::hash_map::RandomState;
use std::hash::Hash;
use crate::shared::{Hooks, Hook};

#[derive(Debug)]
struct Setting {
    name: String,
    value: String,
    value_type: SlothSettingsType,
}

#[derive(Debug)]
struct TranslatableSettingItem {
    name: String,
    content: String,
    lang: String
}

#[derive(Debug)]
struct TranslatableSetting {
    setting: HashMap<String, TranslatableSettingItem>
}

#[derive(Debug)]
struct Menu {

}

#[derive(Debug)]
struct MenuItem {

}

#[derive(Debug)]
struct Language {
    uuid: String,
    long_name: String,
    short_name: String,
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

pub(crate) fn prepare_single_post(conn: &mut Client, uuid: &PyDict, theme_path: String, output_path: String) {
    let general_settings = prepare_settings(conn);
    let translated_settings = prepare_translatable_settings(conn);
    let hooks = Hooks {
        head: Vec::new(),
        footer: Vec::new()
    };

    // get menus
    let menus = get_menus(conn);
    // get languages
    let languages = get_languages(conn);
    // set footer
    get_footer(conn);
    // set theme
    set_theme();
    // set feed tags
    set_feed_tags();
}

fn prepare_settings(conn: &mut Client) -> HashMap<String, Setting> {
    let mut settings: HashMap<String, Setting> = HashMap::new();
    if let Some(setting) = set_individual_setting(
        conn,
        String::from("active_theme"),
        Some(String::from("themes")),
        None,
    ) {
        settings.insert(setting.name.clone(), setting);
    }
    if let Some(setting) = set_individual_setting(
        conn,
        String::from("main_language"),
        None,
        None,
    ) {
        settings.insert(setting.name.clone(), setting);
    }

    if let Some(setting) = set_individual_setting(
        conn,
        String::from("main_language"),
        None,
        None,
    ) {
        settings.insert(setting.name.clone(), setting);
    }

    if let Some(setting) = set_individual_setting(
        conn,
        String::from("number_rss_posts"),
        None,
        None,
    ) {
        settings.insert(setting.name.clone(), setting);
    }

    if let Some(setting) = set_individual_setting(
        conn,
        String::from("site_url"),
        None,
        None,
    ) {
        settings.insert(setting.name.clone(), setting);
    }

    if let Some(setting) = set_individual_setting(
        conn,
        String::from("api_url"),
        None,
        Some(String::from("sloth_api_url")),
    ) {
        settings.insert(setting.name.clone(), setting);
    }

    settings
}

fn set_individual_setting(
    conn: &mut Client,
    setting_name: String,
    settings_type: Option<String>,
    alternate_name: Option<String>
) -> Option<Setting> {
    let sst: String;
    match settings_type {
        Some(s) => sst = s,
        None => sst = String::from("sloth")
    }

    let res = conn.query_one("SELECT settings_name, settings_value, settings_value_type
                                FROM sloth_settings WHERE settings_name = $1 AND settings_type = $2",
                             &[&setting_name, &sst]
    );
    return match res {
        Ok(row) => {
            if let Some(name) = alternate_name {
                Some(Setting {
                    name,
                    value: row.get("settings_value"),
                    value_type: row.get("settings_value_type"),
                })
            } else {
                Some(Setting {
                    name: row.get("settings_name"),
                    value: row.get("settings_value"),
                    value_type: row.get("settings_value_type"),
                })
            }
        },
        Err(e) => {
            None
        }
    }
}

fn prepare_translatable_settings(conn: &mut Client) -> HashMap<String, TranslatableSetting> {
    let mut translatable_settings : HashMap<String, TranslatableSetting> = HashMap::new();

    translatable_settings.insert(
        String::from("sitename"),
        set_translatable_setting(conn, String::from("sitename")));
    translatable_settings.insert(
        String::from("description"),
        set_translatable_setting(conn, String::from("description")));
    translatable_settings.insert(
        String::from("sub_headline"),
        set_translatable_setting(conn, String::from("sub_headline")));
    translatable_settings.insert(
        String::from("archive-title"),
        set_translatable_setting(conn, String::from("archive-title")));
    translatable_settings.insert(
        String::from("category-title"),
        set_translatable_setting(conn, String::from("category-title")));
    translatable_settings.insert(
        String::from("tag-title"),
        set_translatable_setting(conn, String::from("tag-title")));

    translatable_settings
}

fn set_translatable_setting(conn: &mut Client, name: String) -> TranslatableSetting {
    let mut setting: HashMap<String, TranslatableSettingItem> = HashMap::new();
    let mut translatable_settings = TranslatableSetting {
        setting: HashMap::new()
    };

    let rows = conn.query("SELECT name, content, lang
                FROM sloth_localized_strings WHERE name = $1;",
                          &[&name]);

    if let Err(e) = rows {
        return translatable_settings
    }

    for row in rows.unwrap() {
        let item = TranslatableSettingItem {
            name: row.get("name"),
            content: row.get("content"),
            lang: row.get("lang")
        };
        translatable_settings.setting.insert(item.lang.clone(), item);
    }

    translatable_settings
}

fn get_menus(conn: &mut Client) -> HashMap<String, Vec<Row>> {
    let mut menus: HashMap<String, Vec<Row>> = HashMap::new();
    let menu_rows = conn.query("SELECT name, uuid FROM sloth_menus;", &[]);
    if let Err(e) = menu_rows {
        return menus;
    }
    for menu_row in menu_rows.unwrap() {
        let menu_items = conn.query("SELECT title, url FROM sloth_menu_items WHERE menu = $1", &[&menu_row.get("uuid")]);
        if let Err(e) = menu_items {
            continue;
        }
        menus.insert(menu_row.get("name").unwrap(), menu_items.unwrap());
    }
    menus
}

fn get_languages(conn: &mut Client) -> Vec<Language> {
    let mut languages: Vec<Language> = Vec::new();

    languages
}

fn get_footer(conn: &mut Client) {

}

fn set_theme() {

}

fn set_feed_tags() {

}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

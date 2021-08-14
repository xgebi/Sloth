use postgres::Client;
use std::collections::HashMap;
use std::error::Error;
use std::string::String;
use std::sync::Arc;
use pyo3::types::PyDict;
use postgres_types::{ToSql, FromSql};

#[derive(Debug)]
struct Setting {
    name: String,
    value: String,
    value_type: SlothSettingsType,
}

struct TranslatableSetting {
    setting: HashMap<String, Setting>
}

#[derive(Debug, ToSql, FromSql)]
#[postgres(name = "sloth_settings_type")]
enum SlothSettingsType {
    #[postgres(name = "boolean")]
    boolean,
    #[postgres(name = "text")]
    text,
    #[postgres(name = "text-long")]
    text_long,
    #[postgres(name = "select")]
    select
}

pub(crate) fn prepare_single_post(mut conn: Client, uuid: &PyDict, theme_path: String, output_path: String) {
    let general_settings = prepare_settings(&mut conn);
    //let translated_settings = prepare_translatable_settings();
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
    match res {
        Ok(row) => {
            return if let Some(name) = alternate_name {
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
            return None;
        }
    }
}

fn prepare_translatable_settings() -> HashMap<String, TranslatableSetting> {
    HashMap::new()
}

fn set_translatable_setting(mut conn: Client, name: String) {
    // if let Some(sst) = settings_type {
    //     set_settings_type = sst;
    //}

    // conn.query("SELECT uuid, name, content, lang
    //             FROM sloth_localized_strings WHERE name = %s;",
    //                &[&name]
    // )?;
    //
    // for row in client.query("SELECT foo FROM bar WHERE baz = $1", &[&baz])? {
    //     let foo: i32 = row.get("foo");
    //     println!("foo: {}", foo);
    // }
    //
    // Setting {
    //     name: row.get("settings_name"),
    //     value: row.get("settings_value"),
    //     value_type: row.get("settings_value_type")
    // };
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}

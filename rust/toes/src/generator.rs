use postgres::Client;
use std::collections::HashMap;
use std::error::Error;
use std::string::String;
use std::sync::Arc;
use pyo3::types::PyDict;

#[derive(Debug)]
struct Setting {
    name: String,
    value: String,
    value_type: String,
}

struct TranslatableSetting {
    setting: HashMap<String, Setting>
}

pub(crate) fn prepare_single_post(mut conn: Client, uuid: &PyDict, theme_path: String, output_path: String) {
    let general_settings = prepare_settings(&mut conn);
    //let translated_settings = prepare_translatable_settings();
}

fn prepare_settings(conn: &mut Client) -> HashMap<String, Setting> {
    let mut settings = HashMap::new();
    if let Some(setting) = set_individual_setting(
        conn,
        String::from("active_theme"),
        Some(String::from("themes")),
        None,
    ) {
        settings.insert(String::from("active_theme"), setting);
    }
    if let Some(setting) = set_individual_setting(
        conn,
        String::from("main_language"),
        None,
        None,
    ) {
        settings.insert(String::from("main_language"), setting);
    }
    if settings.contains_key("main_language") {
        println!("{:?}", settings.get("main_language"));
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

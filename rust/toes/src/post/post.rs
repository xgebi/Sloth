use std::collections::HashMap;
use postgres::{Client, Error, Row};
use crate::post::post_struct::Post;
use crate::post::settings_structs::Menu;

pub(crate) fn prepare_post(connection: Client, post_data: Post) {
    // prepare settings
    // get post type
    // set output path
    // get related posts
    // if not protected generate post
    // if not protected and archive enabled regenerate archive
    // if not protected and tags enabled regenerate tags
    // if not protected and categories enabled regenerate categories
    // if not protected generate home
    // if protected check if post files exist (if they exist, delete them)
}

pub(crate) fn prepare_settings(connection: Client) {
    // get general settings
    // get translated settings
    // get menus
    // get languages
    // set hooks
    // get footer
    // set theme
    // set feed tags
}

fn get_menus(conn: &mut Client) -> Vec<Menu> {
    let mut menus: Vec<Menu> = Vec::new();
    let menu_rows = conn.query("SELECT name, uuid FROM sloth_menus;", &[]);
    match menu_rows {
        Ok(rows) => {
            for menu_row in rows {
                let name: &str = menu_row.get("name");
                let uuid: &str = menu_row.get("uuid");
                let menu = Menu::new(name.to_string(), uuid.to_string());
                let menu_items = conn.query("SELECT title, url FROM sloth_menu_items WHERE menu = $1", &[&menu.name]);
                // match menu_items {
                //     Err(_) => {
                //         continue;
                //     }
                //     Ok(items) => {
                //         menu.set_item(&items);
                //     }
                // }
                // menus.push(menu);
            }
        }
        Err(_) => { println!("Can't access the menu") }
    }
    menus
}
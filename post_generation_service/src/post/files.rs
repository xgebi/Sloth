use std::path::Path;
use fs_extra::{copy_items, dir};
use sloth_config_lib::get_config;
use common_db_lib::database::connect;

pub(crate) fn copy_assets() -> bool {
    let conf_result = get_config();
    let connexion_result = connect();
    if conf_result.is_err() || connexion_result.is_err() {
        return false;
    }
    let conf = conf_result.unwrap();
    let mut connexion = connexion_result.unwrap();

    let row_result = connexion.query_one("SELECT settings_value FROM sloth_settings WHERE settings_name = 'active_theme';", &[]);
    if let Ok(row) = row_result {
        if row.is_empty() {
            return false;
        }
        let source = Path::new((conf.cms.theme_dir + row.get(0) + "/assets").as_str());
        let target = Path::new((conf.cms.site_dir + "/assets").as_str());

        let options = dir::CopyOptions::new(); //Initialize default values for CopyOptions

        return copy_items(&vec![source], target, &options).is_ok();

    }

    false
}
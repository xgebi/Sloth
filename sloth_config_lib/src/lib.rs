use serde::{Deserialize, Serialize};
use std::env;
use confy::ConfyError;

pub fn get_config() -> Result<SlothConfig, ConfyError> {
    let config_file = env::var("SLOTH_CONFIG").ok();
    if let Some(file_path) = config_file {
        let path = Path::new(&file_path).to_owned();
        if path.exists() {
            return confy::load_path(Path::new(&file_path));
        }
    }
    Err(())
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SlothConfig {
    database: DatabaseConfig,
    post_generation_service: ServiceConfig,
    auth_service: ServiceConfig,
    cms: CmsConfig
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DatabaseConfig {
    url: String,
    port: u8,
    username: String,
    password: String
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServiceConfig {
    url: String,
    port: u8
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CmsConfig {
    theme_dir: String,
    site_dir: String,
}

impl Default for SlothConfig {
    fn default() -> Self {
        Self {
            database: DatabaseConfig {
                url: String::new(),
                port: 0,
                username: String::new(),
                password: String::new(),
            },
            post_generation_service: ServiceConfig {
                url: String::new(),
                port: 0,
            },
            auth_service: ServiceConfig {
                url: String::new(),
                port: 0,
            },
            cms: CmsConfig {
                theme_dir: String::new(),
                site_dir: String::new(),
            }
        }
    }
}

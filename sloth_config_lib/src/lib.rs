use serde::{Deserialize, Serialize};
use std::env;
use std::path::Path;
use confy::ConfyError;

pub fn get_config() -> Result<SlothConfig, ()> {
    let config_file = env::var("SLOTH_CONFIG").ok();
    if let Some(file_path) = config_file {
        let path = Path::new(&file_path).to_owned();
        if path.exists() {
            let loaded_config: Result<SlothConfig, ConfyError> = confy::load_path(Path::new(&file_path)) ;
            match loaded_config {
                Ok(c) => { return Ok(c); }
                Err(e) => {
                    println!("{:?}", e);
                    return Err(());
                }
            }
        }
    }
    println!("error");
    Err(())
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SlothConfig {
    pub database: DatabaseConfig,
    pub post_generation_service: ServiceConfig,
    pub auth_service: ServiceConfig,
    pub cms: CmsConfig
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DatabaseConfig {
    pub url: String,
    pub port: u16,
    pub dbname: String,
    pub username: String,
    pub password: String
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ServiceConfig {
    pub url: String,
    pub port: u16
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CmsConfig {
    pub theme_dir: String,
    pub site_dir: String,
    pub token: String
}

impl Default for SlothConfig {
    fn default() -> Self {
        Self {
            database: DatabaseConfig {
                url: String::new(),
                port: 0,
                dbname: String::new(),
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
                token: String::new(),
            }
        }
    }
}

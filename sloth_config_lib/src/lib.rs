use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct SlothConfig {
    database: DatabaseConfig,
    post_generation_service: ServiceConfig,
    auth_service: ServiceConfig,
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
        }
    }
}

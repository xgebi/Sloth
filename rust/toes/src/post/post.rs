use postgres::Client;
use crate::post::post_struct::Post;

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

pub(crate) fn prepare_post(connection: Client, post_data: Post) {
    // prepare settings


}


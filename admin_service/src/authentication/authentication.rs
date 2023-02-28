use actix_web::{Error, HttpResponse, web};
use deadpool_postgres::Pool;
use tokio_postgres::Client;

pub async fn serve_login_page(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
    todo!("Should serve login page")
    // 1. check if already logged in
    // 2. if logged in redirect to /dashboard
    // 3. else serve login page
        // a. check for error query
        // b. open static file
        // c. pass it to post_generation service
        // d. return rendered template
}

pub async fn process_login(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
    todo!("Should process login")
    // 1. connect to database
    // 2. fetch password hash from database
    // 3. find out algorithm
    // 4. compare password with the hash if good:
    //      I. if hash algorithm is bcrypt rehash password in argon
    //          a. update hash in db
    //      II. update token in database
    //      III. redirect to dashboard
    // 5. in case of no match redirect to login
}

pub async fn process_logout(
        user: web::Json<User>,
        db_pool: web::Data<Pool>,
    ) -> Result<HttpResponse, Error> {
    todo!("Should process login")
    // 1. delete auth cookie
    // 2. connect to database
    // 3. remove auth token from db
    // 4. disconnect from database
    // 5. redirect to login
}
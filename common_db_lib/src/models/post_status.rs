pub enum PostStatus {
    Published,
    Draft,
    Deleted,
    Scheduled,
    Protected
}

impl PostStatus {
    fn value(&self) -> String {
        match *self {
            PostStatus::Published => String::from("published"),
            PostStatus::Draft => String::from("draft"),
            PostStatus::Deleted => String::from("deleted"),
            PostStatus::Scheduled => String::from("scheduled"),
            PostStatus::Protected => String::from("protected"),
        }
    }
}
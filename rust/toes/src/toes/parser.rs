use mocktopus::macros::mockable;

#[mockable]
pub(crate) fn mocked_function(i: i8) -> i8 {
    i
}
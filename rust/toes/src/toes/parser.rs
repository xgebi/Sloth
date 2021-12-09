#[cfg(test)]
use mocktopus::macros::*;

#[mockable]
pub(crate) fn mocked_function(i: i8) -> i8 {
    i
}
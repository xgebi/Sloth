#[derive(Default, Debug)]
pub(crate) struct Setting {
    name: String,
    value: String,
    value_type: SlothSettingsType,
}

#[derive(Default, Debug)]
pub(crate) struct TranslatableSettingItem {
    name: String,
    content: String,
    lang: String
}
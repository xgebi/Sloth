# Theme API

## `post` object

* `uuid`
    * post unique identifier
* `slug`
    * name without spaces and special characters used in links &c.
* `author_name`
    * name of the article's author
* `author_uuid`
    * unique identifier of the article's author
* `title`
    * article's title
* `content`
    * main content of the article
* `excerpt`
    * article's excerpt
* `css`
    * post styles, they don't need to be inlined in a theme as if this field is not empty a style file is generated
* `js`
    * post's scripts, they don't need to be inlined in a theme as if this field is not empty a script file is generated
* `use_theme_cs`
    * for writer this is an indicator that theme's styles should/shouldn't be used
* `use_theme_js`
    * for writer this is an indicator that theme's styles should/shouldn't be used
* `publish_date`
    * timestamp of publishing date
* `publish_date_formatted`, `publish_date_formatted`, `publish_timedate_formatted`
    * formatted publishing date
* `updated_date`
    * timestamp of update date
* `update_date_formatted`
    * formatter update date
* `post_status`
    * post status
* `post_type_slug`
    * slug of post's post type
* `approved`
    * indicator if imported post has been approved
* `thumbnail`
    * link to thumbnail
* `thumbnail_alt`
    * alternative text for thumbnail
* `language_variants`
    * list of language variants
* `original_lang_entry_uuid`
    * unique identifier of original post (not translation)
* `lang`
    * language of the post
* `format_uuid`
    * post format's unique identifier
* `format_slug`
    * post format's slug
* `format_name`
    * post format's name
* `meta_description`
    * description that goes to `<meta name="description" />`
* `twitter_description`
    * description for social media, similar to `meta_description'
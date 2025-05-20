ALTER TABLE sloth_posts ADD COLUMN thumbnail_alt text;
UPDATE sloth_posts SET thumbnail_alt = (SELECT alt FROM sloth_media_alts WHERE sloth_posts.thumbnail = sloth_media_alts.media AND sloth_posts.lang = sloth_media_alts.lang);
UPDATE sloth_taxonomy SET slug = LOWER(slug);
ALTER TABLE sloth_analytics ADD COLUMN user_agent text;
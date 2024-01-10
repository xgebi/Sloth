SELECT content, section_type, position
FROM sloth_post_sections
WHERE post = $1
ORDER BY position;
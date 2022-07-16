UPDATE sloth_post_formats SET slug = 'none';

UPDATE
    sloth_posts as sp
SET post_format = spf.uuid
FROM sloth_post_formats as spf
WHERE sp.post_type = spf.post_type;
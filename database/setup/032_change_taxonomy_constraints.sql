ALTER TABLE public.sloth_post_taxonomies
    DROP CONSTRAINT post_type_fkey;

ALTER TABLE public.sloth_post_taxonomies
    DROP CONSTRAINT taxonomy_fkey;

ALTER TABLE public.sloth_post_taxonomies
    ADD CONSTRAINT post_type_fkey FOREIGN KEY (post)
        REFERENCES sloth_posts (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE;

ALTER TABLE public.sloth_post_taxonomies
    ADD CONSTRAINT taxonomy_fkey FOREIGN KEY (taxonomy)
        REFERENCES sloth_taxonomy (uuid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE;
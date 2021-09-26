ALTER TABLE sloth_forms ALTER COLUMN name SET NOT NULL;
ALTER TABLE sloth_forms DROP COLUMN slug;
ALTER TABLE sloth_form_fields ADD COLUMN type varchar(20);
ALTER TABLE sloth_form_fields ADD COLUMN  is_required boolean;
ALTER TABLE sloth_form_fields ALTER COLUMN is_childless SET DEFAULT true;
ALTER TABLE sloth_form_fields ADD COLUMN label text;
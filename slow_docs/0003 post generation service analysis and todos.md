# Post generation service analysis and todos

## pgs_common
This package has two files, `node` and `patterns`. `node` file contains functionality around nodes. `pattern` have regular expression to detect certain patterns in text.

## pgs_slothmark

This package parses Sloth's dialect of Markdown.

## pgs_toes

This packages parses toe templates. At the moment it is missing a lot of implementations.

Variable scope seems to be the only complete part

## Todos

- [ ] add tests for patterns in `pgs_common` 
- [ ] fix tests in `pgs_slothmark`
  - [ ] `bold_italic_content_b`
  - [ ] `bold_italic_content_c`
  - [ ] `bold_italic_content_d`
  - [ ] `bold_italic_content_e`
- [ ] check completeness of tests in `pgs_slothmark`
  - [ ] follow up with more todos
- [ ] check completeness of tests in `pgs_toes/parser`
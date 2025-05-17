
import {Row, RowList} from "postgres";
import sql from "@/app/db/db";
import {FullPost, PostLibrary, PostSection} from "@/app/interfaces/post";

export async function getPosts(limit = -1): Promise<RowList<Row[]>> {
	const limitStr = limit >= 0 ? sql`LIMIT ${limit}` : sql``;
	return sql`
      select title, uuid, post_type
      from sloth_posts ${limitStr};
	`;
}

export async function getPostsByType(postTypeId: string): Promise<RowList<Row[]>> {
	return sql`
      select title, uuid, post_type, publish_date, update_date
      from sloth_posts WHERE post_type = ${postTypeId}
      order by update_date DESC;
	`;
}

export async function getFullPost(postId: string): Promise<Row | undefined> {
	const fetchedPost = await sql`
    select uuid, original_lang_entry_uuid, lang, slug, post_type, author, title, content, excerpt, css, use_theme_css, js, use_theme_js, thumbnail, publish_date, update_date, post_status, post_format, imported, import_approved, password, meta_description, twitter_description, pinned
    from sloth_posts WHERE uuid = ${postId};
  `;
	const postRow = fetchedPost.pop();
	const post = postRow as FullPost;
	if (post) {
		const fetchedSections = await sql`
			select uuid, content, section_type, position from sloth_post_sections
			where post = ${postId} order by position;
		`;
		if (!post.sections) {
			post.sections = [];
		}
		fetchedSections.forEach((section) => {
			post.sections.push(section as PostSection)
		});

		const fetchedLibraries = await sql`
			select library, hook_name from sloth_post_libraries
			where post = ${postId};
		`;
		if (!post.libraries) {
			post.libraries = [];
		}
		fetchedLibraries.forEach((library) => {
			post.libraries.push(library as PostLibrary)
		});
	}
	return post;
}

/**
 * Suspense component from react. Shows fallback content when data is being loaded
 */
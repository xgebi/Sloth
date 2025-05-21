
import {Row} from "postgres";
import sql from "@/app/db/db";
import {FullPost, PostLibrary, PostSection} from "@/app/interfaces/post";
import {simpleGet} from "@/app/repository/fetch";
import {cookies} from "next/headers";
import {ErrorMessage} from "@/app/interfaces/error-message";
import {Message} from "@/app/interfaces/message";

export async function fetchPostsByType(postTypeId: string) {
	return simpleGet(`/api/post/${postTypeId}`);
}

export async function fetchFullPost(postId: string) {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		const result = await fetch(`${process.env['BACKEND_URL']}/api/post/${postId}`, {
			method: "GET",
			headers: {
				'authorization': `${cookie.displayName}:${cookie.uuid}:${cookie.token}`
			},
		});
		console.log('gdi', result.body);
		const resultObj: object = await result.json();
		console.log('abc', resultObj);
		if (resultObj.hasOwnProperty('error')) {
			return (resultObj as ErrorMessage);
		}
		return resultObj as Message;
	}
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
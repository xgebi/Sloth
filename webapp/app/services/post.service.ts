import 'server-only'

import {
	fetchPostsByType,
	getFullPost as dbGetPost,
} from "@/app/repository/posts.repository";
import {FullPost, Post} from "@/app/interfaces/post";
import {ErrorMessage} from "@/app/interfaces/error-message";

export async function getPostsByType(ptId: string) {
	const fetchedResult = await fetchPostsByType(ptId);
	if (fetchedResult.hasOwnProperty('error')) {
		return fetchedResult as ErrorMessage
	}
	return fetchedResult as Post[];
}

export async function getFullPost(postId: string): Promise<FullPost | undefined> {
	const fetchedResult = await dbGetPost(postId);
	return fetchedResult ? fetchedResult as FullPost : undefined;
}
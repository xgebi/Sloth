import {getFullPost as dbGetPost, getPosts as dbGetPosts, getPostsByType as dbGetPostsByType} from "@/app/repository/posts.repository";
import {FullPost, Post} from "@/app/interfaces/post";

export async function getPosts(limit = -1) {
	const fetchedResult = await dbGetPosts(limit);
	const result: Post[] = [];
	for (const row of fetchedResult) {
		result.push(row as Post);
	}
	return result;
}

export async function getPostsByType(ptId: string) {
	const fetchedResult = await dbGetPostsByType(ptId);
	const result: Post[] = [];
	for (const row of fetchedResult) {
		result.push(row as Post);
		if (result[result.length - 1].publish_date) {
			result[result.length - 1].publish_date = new Date(result[result.length - 1].publish_date as number | Date);
		}
		result[result.length - 1].update_date = new Date(result[result.length - 1].update_date)
	}
	return result;
}

export async function getFullPost(postId: string): Promise<FullPost | undefined> {
	const fetchedResult = await dbGetPost(postId);
	return fetchedResult ? fetchedResult as FullPost : undefined;
}
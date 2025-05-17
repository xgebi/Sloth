import {getPostTypes as dbGetPostTypes, getPostType as dbGetPostType} from "@/app/repository/post-types.repository";
import PostType from "@/app/interfaces/post-type";

export async function getPostTypes() {
	const fetchedResult = await dbGetPostTypes();
	const result: PostType[] = [];
	for (const row of fetchedResult) {
		result.push(row as PostType);
	}
	return result;
}

export async function getPostType(ptId: string) {
	const fetchedResult = await dbGetPostType(ptId);
	return fetchedResult ? fetchedResult as PostType : undefined;
}
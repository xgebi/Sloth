import {getPostType} from "@/app/services/post-type.service";
import {getPostsByType} from "@/app/services/post.service";
import {getLanguageData} from "@/app/services/language.service";
import Language from "@/app/interfaces/language";
import {PostTable} from "@/app/(app)/post-types/[postTypeId]/components/post-table";
import {Post} from "@/app/interfaces/post";
import {formatDate} from "@/app/utilities/date";

type PostTypePageParams = Promise<{postTypeId: string}>

export default async function SettingsPage({ params }: { params: PostTypePageParams }) {
	const uuid = (await params).postTypeId;
	const postType = await getPostType(uuid);
	const posts = await getPostsByType(uuid);
	const languages = await getLanguageData();
	const mainLanguage = (languages as Language[]).find((lang) => lang.default);

	if (!posts.hasOwnProperty("error")) {
		for (const post of posts as Post[]) {
			post.formatedPublishDate = formatDate(post.publish_date);
			post.formatedUpdateDate = formatDate(post.update_date);
		}
		return (
			<div>
				<PostTable mainLanguage={mainLanguage} languages={languages} posts={posts as Post[]} postType={postType}></PostTable>
			</div>
		)
	}
	return <div>No posts</div>
}
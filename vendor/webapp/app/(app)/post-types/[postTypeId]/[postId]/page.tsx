import {getTaxonomyKindOfTypeByPostType} from "@/app/services/taxonomy.service";
import styles from './post.module.css';
import {PostEditor} from "./components/post-editor";
import {createEmptyFullPost, FullPost} from "@/app/interfaces/post";
import {getFullPost} from "@/app/services/post.service";
import {getMedia} from "@/app/services/media.service";
import {getLibraries} from "@/app/services/library.service";
type PostPageParams = Promise<{postId: string, postTypeId: string}>

export default async function PostPage({ params }: { params: PostPageParams }) {
	const postId = (await params).postId;
	const postTypeId = (await params).postTypeId;
	// fetch list of categories
	const categories = await getTaxonomyKindOfTypeByPostType(postTypeId, "category");
	// fetch list of libraries
	const libraries = await getLibraries();
	// fetch list of images
	const images = await getMedia();
	let post: FullPost = createEmptyFullPost();
	if (postId.toLocaleLowerCase() !== "new") {
		const fetchedPost = await getFullPost(postId);
		if (fetchedPost) {
			post = fetchedPost;
		}
		// fetch tags & categories
	} else {
		post.uuid = "new";
		post.post_status = "draft";
	}
	return (
		<main className={styles.main}>
			<PostEditor post={post} media={images} categories={categories} libraries={libraries}/>
		</main>
	)
}

/*
		import {notFound} from "next/navigation";
		if (!post) {
			notFound();
		}
		revalidatePath(<url>) // revalidates path
		 */
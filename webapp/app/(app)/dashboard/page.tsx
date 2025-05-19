import styles from './dashboard.module.css';
import {getDashboardInformation} from "@/app/services/dashboard.service";
import PostBox from "@/app/(app)/dashboard/components/post-box";

export default async function DashboardPage() {
	const posts = await getDashboardInformation();
	console.log(posts);
	return (
		<main className={styles.main}>
			<h1>Dashboard page</h1>

			<section className={styles.boxes}>
				<PostBox posts={posts.recentPosts} name={"Latest posts"} ></PostBox>
				<PostBox posts={posts.drafts} name={"Drafts"} ></PostBox>
			</section>
		</main>
	)
}
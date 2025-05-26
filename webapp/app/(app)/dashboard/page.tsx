import styles from './dashboard.module.css';
import {getDashboardInformation} from "@/app/services/dashboard.service";
import PostBox from "@/app/(app)/dashboard/components/post-box";
import MessageBox from "@/app/(app)/dashboard/components/message-box";
import {checkLoggingCookie} from "@/app/common/cookie-handling";

export default async function DashboardPage() {
	const posts = await getDashboardInformation();
	if (posts.hasOwnProperty('error')) {
		return <main>{posts.error}</main>
	}
	await checkLoggingCookie();
	return (
		<main className={styles.main}>
			<h1>Dashboard page</h1>

			<section className={styles.boxes}>
				<PostBox posts={posts.recentPosts} name={"Latest posts"} ></PostBox>
				<PostBox posts={posts.drafts} name={"Drafts"} ></PostBox>
				<PostBox posts={posts.upcomingPosts} name={"Upcoming"} ></PostBox>
				<MessageBox messages={posts.messages}></MessageBox>
			</section>
		</main>
	)
}
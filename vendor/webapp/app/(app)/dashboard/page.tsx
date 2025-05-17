import Link from "next/link";
import styles from './dashboard.module.css';
import {getPosts} from "@/app/services/post.service";

export default async function DashboardPage() {
	const posts = await getPosts(10);
	return (
		<main className={styles.main}>
			<h1>Dashboard page</h1>

			<section className={styles.boxes}>
				<section className={styles.card}>
					<h2>Latest posts</h2>
					<hr />
					{posts.map((post) => {
						return (
							<article key={post.uuid}>
								<h3><a href={`/post-types/${post.post_type}/${post.uuid}`}>{post.title}</a></h3>
							</article>
						)
					})}
				</section>
					<section className={styles.card}>
					<h2>Last edited</h2>
					<hr />
					{posts.map((post) => {
						return (
							<article key={post.uuid}>
								<h3>{post.title}</h3>
							</article>
						)
					})}
				</section>
			</section>
		</main>
	)
}
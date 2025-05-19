import styles from "@/app/(app)/dashboard/dashboard.module.css";

export default function PostBox({ posts, name }) {
	return (
		<section className={styles.card}>
			<h2>{name}</h2>
			<hr />
			{posts.length === 0 && <div>No posts</div>}
			{posts.map((post) => {
				return (
					<article key={post.uuid}>
						<h3><a href={`/post-types/${post.post_type}/${post.uuid}`}>{post.title}</a></h3>
					</article>
				)
			})}
		</section>
	)
}
import styles from "@/app/(app)/dashboard/dashboard.module.css";
import commonBoxStyles from './common-box.module.css';

interface PostBoxProps {
	posts: [{
		uuid: string,
		title: string,
		post_type: string,
		publishDate: number,
		formattedPublishDate: string
	}],
	name: string,
}

export default function PostBox({ posts, name }: PostBoxProps) {
	return (
		<section className={commonBoxStyles.card}>
			<h2>{name}</h2>
			<hr />
			{posts.length <= 0 && <div className={commonBoxStyles['no-posts-message']}>No posts</div>}
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
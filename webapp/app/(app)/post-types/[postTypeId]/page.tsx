import {getPostType} from "@/app/services/post-type.service";
import {getPostsByType} from "@/app/services/post.service";
import Link from "next/link";
import styles from './post-type.module.css'

function formatDate(d: Date | null | number) {
	if (!d) {
		return '';
	}
	if (typeof d === "number") {
		d = new Date(d);
	}
	return `${d.getFullYear()}-${d.getMonth() <= 9 ? `0${d.getMonth()}` : d.getMonth()}-${d.getDay() <= 9 ? `0${d.getDay()}` : d.getDay()} ${d.getHours() <= 9 ? `0${d.getHours()}` : d.getHours()}:${d.getMinutes() <= 9 ? `0${d.getMinutes()}` : d.getMinutes()}`;
}

export default async function SettingsPage({ params }: { params: { postTypeId : string }}) {
	const uuid = (await params).postTypeId;
	const postType = await getPostType(uuid);
	const posts = await getPostsByType(uuid);
	if (postType) {
		return (
			<main>
				<h1>{postType.display_name}</h1>
				<section>
					<label htmlFor="language-picker">Choose language:</label>
					<select id="language-picker">
						<option>English</option>
						<option>German</option>
						<option>Spanish</option>
					</select>
					<button>Filter language</button>
				</section>
				<table className={styles['post-table']}>
					<thead>
						<tr>
							<th>Title</th>
							<th>Published date</th>
							<th>Updated date</th>
							<th>Edit</th>
						</tr>
					</thead>
					<tbody>
					{posts.map((post) => (
						<tr key={post.uuid}>
							<td>{post.title}</td>
							<td>{formatDate(post.publish_date)}</td>
							<td>{formatDate(post.update_date)}</td>
							<td><Link href={`/post-types/${uuid}/${post.uuid}`}>edit</Link></td>
						</tr>
					))}
					</tbody>
				</table>
			</main>
		)
	}
	return (
		<h1>Wrong post type</h1>
	)
}
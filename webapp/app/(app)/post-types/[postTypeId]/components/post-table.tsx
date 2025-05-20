"use client";

import {LanguagePicker} from "@/app/(app)/post-types/[postTypeId]/components/language-picker";
import styles from "@/app/(app)/post-types/[postTypeId]/post-type.module.css";
import Link from "next/link";
import {formatDate} from "@/app/utilities/date";
import Language from "@/app/interfaces/language";
import {ErrorMessage} from "@/app/interfaces/error-message";
import {useEffect, useState} from "react";
import PostType from "@/app/interfaces/post-type";
import {Post} from "@/app/interfaces/post";

type PostTableProps = {
	languages: Language[] | ErrorMessage,
	mainLanguage: Language | undefined,
	postType: PostType | undefined,
	posts: Post[]
}

export function PostTable({ languages, mainLanguage, postType, posts}: PostTableProps) {
	const [currentLanguage, setCurrentLanguage] = useState(mainLanguage);

	function handleCurrentLanguage(uuid: string) {
		const lang = (languages as Language[]).find((lang) => lang.uuid === uuid);
		if (lang) {
			setCurrentLanguage(lang);
		}
	}

	if (postType) {
		return (
			<main>
				<h1>{postType.display_name}</h1>
				<LanguagePicker languages={languages} mainLanguage={currentLanguage} onLanguageChange={handleCurrentLanguage} />
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
					{posts.filter((post) => post.lang === currentLanguage?.uuid).map((post) => (
						<tr key={post.uuid}>
							<td>{post.title}</td>
							<td>{post.formatedPublishDate}</td>
							<td>{post.formatedUpdateDate}</td>
							<td><Link href={`/post-types/${postType.uuid}/${post.uuid}`}>edit</Link></td>
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
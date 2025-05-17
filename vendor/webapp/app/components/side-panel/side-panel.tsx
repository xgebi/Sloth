// 'use client'; // indicates if it's client side component

import styles from "./side-panel.module.css";
import MainNavLink from "./main-nav-link";
import {getPostTypes} from "@/app/services/post-type.service";

export default async function SidePanel() {
	const postTypes = await getPostTypes();

	return (
		<nav className={styles["main-nav"]}>
			<ul>
				<li><MainNavLink href="/dashboard">Dashboard</MainNavLink>
					<ul>
						<li><MainNavLink href="/dashboard/statistics">Statistics</MainNavLink></li>
					</ul>
				</li>
				<li className={styles.open}>
					Posts Types
					<ul>
						{postTypes.map((pt) => (
										<li key={pt.uuid}>
						<MainNavLink href={`/post-types/${pt.uuid}`}>{pt.display_name}</MainNavLink>
							<ul>
								<li key={`${pt.uuid}-new`}><MainNavLink href={`/post-types/${pt.uuid}/new`}>New post</MainNavLink></li>
								<li key={`${pt.uuid}-tax`}><MainNavLink href={`/post-types/${pt.uuid}/taxonomy`}>Taxonomy</MainNavLink></li>
								<li key={`${pt.uuid}-formats`}><MainNavLink href={`/post-types/${pt.uuid}/post-formats`}>Post formats</MainNavLink></li>
							</ul>
						</li>
						))}
					</ul>
				</li>
				<li><MainNavLink href="/app/settings">Settings</MainNavLink></li>
			</ul>
		</nav>
	)
}
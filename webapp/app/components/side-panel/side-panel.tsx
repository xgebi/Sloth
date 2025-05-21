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
						<li><MainNavLink href="/dashboard/messages" startsWith={true}>Messages</MainNavLink></li>
						<li><MainNavLink href="/dashboard/statistics">Statistics</MainNavLink></li>
					</ul>
				</li>
				<li className={styles.open}>
					Posts Types
					<ul>
						{postTypes.map((pt) => (
										<li key={pt.uuid}>
						<MainNavLink href={`/post-types/${pt.uuid}`} startsWith={true}>{pt.display_name}</MainNavLink>
							<ul>
								<li key={`${pt.uuid}-new`}><MainNavLink href={`/post-types/${pt.uuid}/new`}>New post</MainNavLink></li>
								<li key={`${pt.uuid}-tax`}><MainNavLink href={`/post-types/${pt.uuid}/taxonomy`}>Taxonomy</MainNavLink></li>
								<li key={`${pt.uuid}-formats`}><MainNavLink href={`/post-types/${pt.uuid}/post-formats`}>Post formats</MainNavLink></li>
							</ul>
						</li>
						))}
					</ul>
				</li>
				<li><MainNavLink href="/settings">Settings</MainNavLink>
					<ul>
						{/*when this is not single user CMS, this needs to be guarded/hidden at times*/}
						<li><MainNavLink href={`/settings/users`}>Users</MainNavLink></li>
						<li><MainNavLink href={`/settings/themes`}>Themes</MainNavLink></li>
						<li><MainNavLink href={`/settings/menus`}>Menus</MainNavLink></li>
						<li><MainNavLink href={`/settings/languages`}>Languages</MainNavLink></li>
						<li><MainNavLink href={`/settings/localized`}>Localized name</MainNavLink></li>
						<li><MainNavLink href={`/settings/dev`}>Dev settings</MainNavLink></li>
					</ul>
				</li>
			</ul>
		</nav>
	)
}
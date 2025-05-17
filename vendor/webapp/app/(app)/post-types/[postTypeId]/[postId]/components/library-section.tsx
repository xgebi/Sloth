import styles from "@/app/(app)/post-types/[postTypeId]/[postId]/post.module.css";
import {SyntheticEvent, useState} from "react";
import {PostLibrary} from "@/app/interfaces/post";
import Library from "@/app/interfaces/library";

interface LibrarySectionProps {
	libraryList: Library[],
	postLibraries: PostLibrary[],
	addLibrary: (uuid: string, position: string) => void,
	removeLibrary: (uuid: string) => void
}

export default function LibrarySection({ libraryList, postLibraries, addLibrary, removeLibrary }: LibrarySectionProps) {
	const [library, setLibrary] = useState('');
	const [libraryHook, setLibraryHook] = useState('');

	function localAddLibrary() {
		if (library.length > 0 && libraryHook.length > 0) {
			addLibrary(library, libraryHook);
		}
	}
	function localRemoveLibrary(ev: SyntheticEvent) {
		const library = (ev.target as HTMLSelectElement).dataset['id'];
		if (library) {
			removeLibrary(library);
		}
	}

	function updateSelectedLibrary(ev: SyntheticEvent) {
		const lib = (ev.target as HTMLSelectElement).value;
		setLibrary(lib);
	}

	function updateLibraryHook(ev: SyntheticEvent) {
		const hook = (ev.target as HTMLSelectElement).value;
		setLibraryHook(hook);
	}

	return (
		<div className={styles['external-libraries']}>
						<h2>External libraries</h2>
						<div className={styles['libraries-wrapper']}>
							<div>
								<label htmlFor="libraries-list">Libraries</label>
								<select id="libraries-list" value={library} onChange={updateSelectedLibrary}>
									<option value=""></option>
									{libraryList.map((library) => (
										<option key={library.uuid} value={library.uuid}>{library.name} {library.version}</option>
									))}
								</select>
							</div>
							<div>
								<label htmlFor="library-position">Library position</label>
								<select id="libraries-list" value={libraryHook} onChange={updateLibraryHook}>
									<option value=""></option>
									<option value="header">Header</option>
									<option value="footer">Footer</option>
								</select>
							</div>
							<div>
								<button onClick={localAddLibrary}>Add library</button>
							</div>
						</div>
						{postLibraries.length > 0 && <table>
							<thead>
								<tr>
									<th>
										Library
									</th>
									<th>
										Version
									</th>
									<th>
										Location
									</th>
									<th>
										Removed
									</th>
								</tr>
							</thead>
							<tbody>
							{postLibraries.map((library) => {
								const matchedLibrary = libraryList.find((searchedLibrary) =>
									searchedLibrary.uuid === library.library);
								if (!matchedLibrary) {
									return (<></>);
								}
								return (
									<tr key={library.library}>
										<td>{matchedLibrary?.name}</td>
										<td>{matchedLibrary?.version}</td>
										<td>{library.hook_name}</td>
										<td><button className="danger" data-id={library.library} onClick={localRemoveLibrary}>Remove</button></td>
									</tr>
								);
								})}
							</tbody>
						</table>}
					</div>
	);
}
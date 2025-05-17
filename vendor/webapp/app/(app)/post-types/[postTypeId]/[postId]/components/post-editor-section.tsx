import {PostSection} from "@/app/interfaces/post";
import styles from "@/app/(app)/post-types/[postTypeId]/[postId]/post.module.css";
import {SyntheticEvent} from "react";
import TextareaAutosize from 'react-textarea-autosize';

interface PostEditorSectionProps {
	section: PostSection,
	onSectionTypeUpdated: (uuid: string, type: string) => void,
	onSectionContentUpdated: (uuid: string, content: string) => void,
	onMoveUp: (uuid: string) => void,
	onMoveDown: (uuid: string) => void,
	onDelete: (uuid: string) => void
}
export default function PostEditorSection({ section, onSectionTypeUpdated, onSectionContentUpdated, onMoveUp, onMoveDown, onDelete }: PostEditorSectionProps) {
	function localOnSectionTypeUpdated(ev: SyntheticEvent) {
		const type = ((ev.target as HTMLElement).previousElementSibling as HTMLSelectElement).value;
		onSectionTypeUpdated(section.uuid, type);
	}

	function tempChange(ev: SyntheticEvent) {
		onSectionContentUpdated(section.uuid, (ev.target as HTMLInputElement).value || "");
	}

	function localOnMoveUp() {
		onMoveUp(section.uuid);
	}
	function localOnMoveDown() {
		onMoveDown(section.uuid);
	}
	function localOnDelete() {
		onDelete(section.uuid)
	}

	return (
		<div key={section.uuid} className={styles['article-post-sections']} data-uuid={section.uuid}>
			{section.position === 0 && <h2>Excerpt</h2>}
			{section.position === 1 && <h2>Rest of the article</h2>}
			{section.section_type === "text" && <TextareaAutosize value={section.content} onInput={tempChange}/>}
			{section.section_type === "form" && <input type="text" value={section.content} onInput={tempChange} />}
			<div className={styles['article-post-sections-actions']}>
				<section>
					<select defaultValue={section.section_type}>
						<option value="toc">Table of Content</option>
						<option value="text">Text</option>
						<option value="form">Form</option>
						<option value="image">Image</option>
					</select>
					<button onClick={localOnSectionTypeUpdated}>Change section type</button>
				</section>
				<section>
					<button onClick={localOnMoveUp}>▲</button>
					<button onClick={localOnMoveDown}>▼</button>
					<button onClick={localOnDelete}>Remove section</button>
				</section>
			</div>
		</div>)
}
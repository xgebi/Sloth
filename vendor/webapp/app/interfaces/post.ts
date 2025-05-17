export interface Post {
	title: string,
	uuid: string,
	post_type: string,
	publish_date: number | Date | null,
	update_date: number | Date
}

export interface PostLibrary {
	library: string,
	hook_name: string,
}

export interface PostSection {
	uuid: string,
	content: string,
	section_type: string,
	position: number,
}

export interface FullPost {
	uuid: string,
	original_lang_entry_uuid: string,
	lang: string,
	slug: string,
	post_type: string,
	author: string,
	title: string,
	content: string,
	excerpt: string,
	css: string,
	use_theme_css: boolean,
	js: string,
	use_theme_js: boolean,
	thumbnail: string,
	publish_date: string,
	update_date: number,
	post_status: string,
	post_format: string,
	imported: boolean,
	import_approved: boolean,
	password: string,
	meta_description: string,
	twitter_description: string,
	pinned: boolean,
	sections: PostSection[],
	libraries: PostLibrary[]
}

export function createEmptyFullPost(): FullPost {
	return {
		uuid: "",
		original_lang_entry_uuid: "",
		lang: "",
		slug: "",
		post_type: "",
		author: "",
		title: "",
		content: "",
		excerpt: "",
		css: "",
		use_theme_css: false,
		js: "",
		use_theme_js: false,
		thumbnail: "",
		publish_date: "",
		update_date: 0,
		post_status: "",
		post_format: "",
		imported: false,
		import_approved: false,
		password: "",
		meta_description: "",
		twitter_description: "",
		pinned: false,
		sections: [],
		libraries: []
	};
}
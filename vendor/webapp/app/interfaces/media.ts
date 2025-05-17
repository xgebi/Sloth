export interface Media {
	uuid: string,
	file_path: string,
	wp_id: string,
	added_date: number
	alt: MediaAlt[]
}

export interface MediaAlt {
	uuid: string,
	media: string,
	lang: string,
	alt: string,
}
import {getMedia as dbGetMedia, getMediaAlts} from "@/app/repository/media.repository";
import {Media, MediaAlt} from "@/app/interfaces/media";

export async function getMedia() {
	const fetchedResult = await dbGetMedia();
	const fetchedAlts = await getMediaAlts();
	const alts = [];
	for (const row of fetchedAlts) {
		alts.push(row as MediaAlt);
	}
	const result: Media[] = [];
	for (const row of fetchedResult) {
		const media = row as Media;
		media.alt = alts.filter((alt) => alt.media === media.uuid)
		result.push(media);
	}
	return result;
}
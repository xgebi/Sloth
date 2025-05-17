import {Row, RowList} from "postgres";
import sql from "@/app/db/db";

export async function getMedia(): Promise<RowList<Row[]>> {
	return sql`
      select uuid, file_path, wp_id, added_date
      from sloth_media;
	`;
}

export async function getMediaAlts(): Promise<RowList<Row[]>> {
	return sql`
      select uuid, media, lang, alt
      from sloth_media_alts;
	`;
}
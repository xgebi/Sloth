
import {Row, RowList} from "postgres";
import sql from "@/app/db/db";

export async function getTaxonomyByPostType(postTypeId: string): Promise<RowList<Row[]>> {
	return sql`
      select uuid,
				slug,
				display_name,
				post_type,
				taxonomy_type,
				lang
      from sloth_taxonomy WHERE post_type = ${postTypeId};
	`;
}

export async function getTaxonomyKindOfTypeByPostType(postTypeId: string, taxonomyType: string): Promise<RowList<Row[]>> {
	return sql`
      select uuid,
				slug,
				display_name,
				post_type,
				taxonomy_type,
				lang
      from sloth_taxonomy WHERE post_type = ${postTypeId} AND taxonomy_type = ${taxonomyType};
	`;
}

/**
 * Suspense component from react. Shows fallback content when data is being loaded
 */
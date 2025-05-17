
import { getTaxonomyByPostType as dbGetTaxonomyByPostType, getTaxonomyKindOfTypeByPostType as dbGetTaxonomyKindOfTypeByPostType } from '../repository/taxonomy.repository'
import Taxonomy from "@/app/interfaces/taxonomy";

export async function getTaxonomyByPostType(postTypeId: string) {
	const fetched = await dbGetTaxonomyByPostType(postTypeId);
	const result: Taxonomy[] = [];
	for (const row of fetched) {
		result.push(row as Taxonomy);
	}
	return result;
}

export async function getTaxonomyKindOfTypeByPostType(postTypeId: string, taxonomyType: string) {
	const fetched = await dbGetTaxonomyKindOfTypeByPostType(postTypeId, taxonomyType);
	const result: Taxonomy[] = [];
	for (const row of fetched) {
		result.push(row as Taxonomy);
	}
	return result;
}

/**
 * Suspense component from react. Shows fallback content when data is being loaded
 */
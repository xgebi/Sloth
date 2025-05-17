import {getLibraries as dbGetLibraries} from "@/app/repository/library.repository";
import Library from "@/app/interfaces/library";

export async function getLibraries() {
	const fetchedResult = await dbGetLibraries();
	const result: Library[] = [];
	for (const row of fetchedResult) {
		result.push(row as Library);
	}
	return result;
}
import {Row, RowList} from "postgres";
import sql from "@/app/db/db";

export async function getLibraries(): Promise<RowList<Row[]>> {
	return sql`
      select uuid, name, version, location
      from sloth_libraries;
	`;
}
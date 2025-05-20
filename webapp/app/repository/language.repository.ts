import {simpleGet} from "@/app/repository/fetch";

export async function fetchLanguageData() {
	return simpleGet("/api/languages");
}
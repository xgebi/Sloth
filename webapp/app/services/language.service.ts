import 'server-only'
import {fetchLanguageData} from "@/app/repository/language.repository";
import {ErrorMessage} from "@/app/interfaces/error-message";
import Language from "@/app/interfaces/language";

export async function getLanguageData() {
	const languageData = await fetchLanguageData();
	if (languageData.hasOwnProperty("error")) {
		return languageData as ErrorMessage;
	}
	return languageData as Language[];
}
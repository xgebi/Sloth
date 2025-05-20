"use client";

import Language from "@/app/interfaces/language";
import {ErrorMessage} from "@/app/interfaces/error-message";
import {SyntheticEvent} from "react";

type LanguagePickerProps = {languages: Language[] | ErrorMessage, mainLanguage: Language | undefined, onLanguageChange: (uuid: string) => void}

export function LanguagePicker({ languages, mainLanguage, onLanguageChange }: LanguagePickerProps) {
	if (languages.hasOwnProperty("error")) {
		return <section>Failed to load languages</section>
	}
	return (
		<section>
					<label htmlFor="language-picker">Choose language:</label>
					<select
						id="language-picker"
						value={mainLanguage ? mainLanguage.uuid : ''}
						onChange={(ev: SyntheticEvent)=> onLanguageChange((ev.target as HTMLSelectElement).value)}>
						<option></option>
						{(languages as Language[]).map((lang) => (
							<option key={lang.uuid} value={lang.uuid}>{lang.long_name}</option>
						))}
					</select>
				</section>
	)
}
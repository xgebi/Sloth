import traceback

import psycopg
from typing import List, Dict

from app.repositories.post_repositories import get_other_translations, get_translation_for_original, \
	get_all_translations


def get_translations(*args, connection: psycopg.Connection, post_uuid: str, original_entry_uuid: str, languages: List,
					 **kwargs):
	"""
	PostGenerator: it should deliver available translations (all statuses)
	get_post_data: sort of the same but work differently
	prepare_data_new_post

	:param args:
	:param connection:
	:param post_uuid:
	:param original_entry_uuid:
	:param languages:
	:param kwargs:
	:return:
	"""
	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			translatable = []
			if original_entry_uuid is not None and len(original_entry_uuid) > 0:
				translations = get_other_translations(cur=cur, original_entry_uuid=original_entry_uuid,
													  post_uuid=post_uuid)
			else:
				translations = get_translation_for_original(cur=cur, post_uuid=post_uuid)
			translations = {translation['lang']: translation for translation in translations}
			translated_languages = []
			for language in languages:
				# temp translations is uuid + lang, not list of languages!!!
				if language['uuid'] in translations.keys():
					translated_languages.append({
						'lang_uuid': language['uuid'],
						'post_uuid': translations[language["uuid"]]["uuid"],
						'long_name': language['long_name'],
						'short_name': language['short_name'],
						'slug': translations[language["uuid"]]["slug"],
						'status': translations[language['uuid']]["status"]
					})
				else:
					translatable.append(language)

			return translated_languages, translatable
	except Exception as e:
		print(e)
		traceback.print_exc()
		return [], []


def get_taxonomy_for_post_prepped_for_listing(connection: psycopg.Connection, uuid: str, main_language: Dict,
											  language: Dict, post_type_slug: str) -> (List, List):
	if main_language['settings_value'] == language['uuid']:
		prefix = f'/{post_type_slug}/'
	else:
		prefix = f"/{language['short_name']}/{post_type_slug}/"

	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute(
				"""SELECT st.slug, st.display_name, st.taxonomy_type
					FROM sloth_post_taxonomies AS spt
					INNER JOIN sloth_taxonomy AS st
					ON st.uuid = spt.taxonomy
					WHERE spt.post = %s;""",
				(uuid,)
			)
			all_taxonomies = cur.fetchall()
	except Exception as e:
		print(e)
		traceback.print_exc()
		return [], []
	categories = []
	tags = []

	for taxonomy in all_taxonomies:
		taxonomy.update({
			"url": f"{prefix}{taxonomy['taxonomy_type']}/{taxonomy['slug']}"
		})
		if taxonomy['taxonomy_type'] == "tag":
			tags.append(taxonomy)
		elif taxonomy['taxonomy_type'] == "category":
			categories.append(taxonomy)

	return categories, tags

def get_available_translations(*args, connection: psycopg.Connection, post_uuid: str, languages: List,
					 **kwargs):
	"""
	PostGenerator: it should deliver available translations (all statuses)
	get_post_data: sort of the same but work differently
	prepare_data_new_post

	:param args:
	:param connection:
	:param post_uuid:
	:param original_entry_uuid:
	:param languages:
	:param kwargs:
	:return:
	"""
	try:
		with connection.cursor(row_factory=psycopg.rows.dict_row) as cur:
			translations = get_all_translations(cur=cur, post_uuid=post_uuid)
			translations = {translation['lang']: translation for translation in translations}
			translated_languages = []
			for language in languages:
				# temp translations is uuid + lang, not list of languages!!!
				if language['uuid'] in translations.keys():
					translated_languages.append({
						'lang_uuid': language['uuid'],
						'post_uuid': translations[language["uuid"]]["uuid"],
						'long_name': language['long_name'],
						'short_name': language['short_name'],
						'slug': translations[language["uuid"]]["slug"],
						'status': translations[language['uuid']]["status"]
					})

			return translated_languages
	except Exception as e:
		print(e)
		traceback.print_exc()
		return []
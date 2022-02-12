import psycopg
from typing import List, Dict

from app.repositories.post_repositories import get_other_translations, get_translation_for_original


def get_translations(*args, connection: psycopg.Connection, post_uuid: str, original_entry_uuid: str, languages: List,
                     **kwargs):
    try:
        with connection.cursor() as cur:
            translatable = []
            if original_entry_uuid is not None and len(original_entry_uuid) > 0:
                temp_translations = get_other_translations(cur=cur, original_entry_uuid=original_entry_uuid,
                                                           post_uuid=post_uuid)
            else:
                temp_translations = get_translation_for_original(cur=cur, post_uuid=post_uuid)
            translations = {translation[1]: {
                "uuid": translation[0],
                "lang": translation[1],
                "slug": translation[2],
                "status": translation[3]
            } for translation in temp_translations}
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
        return [], []


def get_taxonomy_for_post_prepped_for_listing(connection: psycopg.Connection, uuid: str, main_language: Dict,
                                              language: Dict) -> (List, List):
    if main_language['settings_value'] == language['uuid']:
        prefix = '/'
    else:
        prefix = f"/{language['short_name']}/"

    try:
        with connection.cursor() as cur:
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
        return [], []
    categories = []
    tags = []

    for taxonomy in all_taxonomies:
        thing = {
            "slug": taxonomy[0],
            "display_name": taxonomy[1],
            "url": f"{prefix}{taxonomy[2]}/{taxonomy[0]}"
        }
        if taxonomy[2] == "tag":
            tags.append(thing)
        elif taxonomy[2] == "category":
            categories.append(thing)

    return categories, tags

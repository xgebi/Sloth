from flask import Blueprint
from psycopg2 import sql
from typing import List

post = Blueprint('post', __name__, template_folder='templates')


def get_translations(*args, connection, post_uuid, original_entry_uuid, languages, **kwargs):
    cur = connection.cursor()
    try:
        translatable = []
        if original_entry_uuid is not None and len(original_entry_uuid) > 0:
            cur.execute(
                sql.SQL("""SELECT uuid, lang, slug, post_status FROM sloth_posts 
                        WHERE (original_lang_entry_uuid=%s AND uuid <> %s) OR (uuid = %s)"""),
                (original_entry_uuid, post_uuid, original_entry_uuid)
            )
        else:
            cur.execute(
                sql.SQL("""SELECT uuid, lang, slug, post_status FROM sloth_posts WHERE original_lang_entry_uuid=%s"""),
                (post_uuid,)
            )
        temp_translations = cur.fetchall()
        translations = {translation[1]: {
            "uuid": translation[0],
            "lang": translation[1],
            "slug": translation[2],
            "status": translation[3]
        } for translation in temp_translations}
        translated_languages = []
        for language in languages:
            if language['uuid'] in translations.keys():  # temp translations is uuid + lang, not list of languages!!!
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


def get_taxonomy_for_post_preped_for_listing(connection, uuid: str, main_language, language) -> (List, List):
    if main_language['settings_value'] == language['uuid']:
        prefix = '/'
    else:
        prefix = f"/{language['short_name']}/"

    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""SELECT st.slug, st.display_name, st.taxonomy_type
                FROM sloth_post_taxonomies AS spt
                INNER JOIN sloth_taxonomy AS st
                ON st.uuid = spt.taxonomy
                WHERE spt.post = %s;"""),
            (uuid, )
        )
        all_taxonomies = cur.fetchall()
    except Exception as e:
        print(e)
        return [], []
    categories = []
    tags = []

    for taxonomy in all_taxonomies:
        thing = {
            "display_name": taxonomy[1],
            "url": f"{prefix}{taxonomy[2]}/{taxonomy[0]}"
        }
        if taxonomy[2] == "tag":
            tags.append(thing)
        elif taxonomy[2] == "category":
            categories.append(thing)

    return categories, tags


from app.post import routes

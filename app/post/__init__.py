from flask import Blueprint
from psycopg2 import sql

post = Blueprint('post', __name__, template_folder='templates')


def get_translations(*args, connection, post_uuid, original_entry_uuid, languages, **kwargs):
    cur = connection.cursor()
    try:
        translatable = []
        if original_entry_uuid is not None and len(original_entry_uuid) > 0:
            cur.execute(
                sql.SQL("""SELECT uuid, lang, slug FROM sloth_posts 
                        WHERE (original_lang_entry_uuid=%s AND uuid <> %s) OR (uuid = %s)"""),
                (original_entry_uuid, post_uuid, original_entry_uuid)
            )
        else:
            cur.execute(
                sql.SQL("""SELECT uuid, lang, slug FROM sloth_posts WHERE original_lang_entry_uuid=%s"""),
                (post_uuid,)
            )
        temp_translations = cur.fetchall()
        translations = {translation[1]: {
            "uuid": translation[0],
            "lang": translation[1],
            "slug": translation[2]
        } for translation in temp_translations}
        translated_languages = []
        for language in languages:
            if language['uuid'] in translations.keys():  # temp translations is uuid + lang, not list of languages!!!
                translated_languages.append({
                    'lang_uuid': language['uuid'],
                    'post_uuid': translations[language["uuid"]]["uuid"],
                    'long_name': language['long_name'],
                    'short_name': language['short_name'],
                    'slug': translations[language["uuid"]]["slug"]
                })
            else:
                translatable.append(language)

        return translated_languages, translatable
    except Exception as e:
        print(e)
        return [], []


from app.post import routes

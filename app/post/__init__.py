from flask import Blueprint
from psycopg2 import sql

post = Blueprint('post', __name__, template_folder='templates')


def get_translations(*args, connection, post_uuid, original_entry_uuid, languages, **kwargs):
    cur = connection.cursor()
    try:
        # Get existing languages
        if original_entry_uuid is not None and len(original_entry_uuid) != 0 and original_entry_uuid != 'None':
            cur.execute(
                sql.SQL(
                    """SELECT lang, uuid, slug FROM sloth_posts 
                    WHERE uuid = %s OR (original_lang_entry_uuid = %s AND uuid <> %s);"""),
                (original_entry_uuid, original_entry_uuid, post_uuid)
            )
        else:
            cur.execute(
                sql.SQL(
                    """SELECT lang, uuid, slug FROM sloth_posts 
                    WHERE original_lang_entry_uuid = %s AND uuid <> %s;"""),
                (post_uuid, post_uuid)
            )
        raw_langs = cur.fetchall()
        translatable_languages = [lang for lang in languages if lang['uuid'] not in [uuid[0] for uuid in raw_langs]]
        translations = [lang for lang in languages if lang['uuid'] in [uuid[0] for uuid in raw_langs]]
        for translated_post in raw_langs:
            for lang in translations:
                if translated_post[0] == lang['uuid']:
                    lang["post"] = translated_post[1]
                    lang["slug"] = translated_post[2]
                    break

        return translations, translatable_languages
    except Exception as e:
        print(e)
        return None, None


from app.post import routes

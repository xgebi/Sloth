from psycopg2 import sql


def get_languages(*args, connection, lang_id, **kwargs):
    cur = connection.cursor()
    temp_languages = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, long_name FROM sloth_language_settings""")
        )
        temp_languages = cur.fetchall()
    except Exception as e:
        print(e)
        return ()

    languages = [{
        "uuid": lang[0],
        "long_name": lang[1]
    } for lang in temp_languages if lang[0] != lang_id]
    current_lang = [{
        "uuid": lang[0],
        "long_name": lang[1]
    } for lang in temp_languages if lang[0] == lang_id][0]

    return current_lang, languages

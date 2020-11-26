from psycopg2 import sql
from typing import Tuple, List, Dict, Any


def get_languages(*args, connection, lang_id: str = "", **kwargs) \
        -> Tuple[Dict[str, Any], List[Dict[str, Any]]] or List[Dict[str, Any]]:
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

    if len(lang_id) != 0:
        languages = [{
            "uuid": lang[0],
            "long_name": lang[1]
        } for lang in temp_languages if lang[0] != lang_id]
        current_lang = [{
            "uuid": lang[0],
            "long_name": lang[1]
        } for lang in temp_languages if lang[0] == lang_id][0]

        return current_lang, languages
    return [{
        "uuid": lang[0],
        "long_name": lang[1]
    } for lang in temp_languages]


def get_default_language(*args, connection, **kwargs) -> Dict[str, str]:
    cur = connection.cursor()
    main_language = []
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, long_name FROM sloth_language_settings 
            WHERE uuid = (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language')""")
        )
        main_language = cur.fetchone()
    except Exception as e:
        print(e)
        return {}

    return {
        "uuid": main_language[0],
        "long_name": main_language[1]
    }

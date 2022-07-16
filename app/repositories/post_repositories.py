import psycopg.cursor
from typing import List


def get_other_translations(cur: psycopg.cursor.Cursor, original_entry_uuid: str, post_uuid: str) -> List:
	if original_entry_uuid is not None and len(original_entry_uuid) > 0:
		cur.execute("""SELECT uuid, lang, slug, post_status as status FROM sloth_posts 
                            WHERE (original_lang_entry_uuid=%s AND uuid <> %s) OR (uuid = %s)""",
					(original_entry_uuid, post_uuid, original_entry_uuid))
		return cur.fetchall()
	return []


def get_translation_for_original(cur: psycopg.cursor.Cursor, post_uuid: str) -> List:
	if post_uuid is not None and len(post_uuid) > 0:
		cur.execute("""SELECT uuid, lang, slug, post_status as status FROM sloth_posts WHERE original_lang_entry_uuid=%s""",
					(post_uuid,)
					)
		return cur.fetchall()
	return []

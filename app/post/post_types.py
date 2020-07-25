from flask import abort
import psycopg2
from psycopg2 import sql, errors


class PostTypes:
    def __init__(self):
        pass

    # Placeholder for the future

    def get_post_type_list(self, connection):
        cur = connection.cursor()
        raw_items = []
        try:
            cur.execute(
                "SELECT uuid, display_name, slug FROM sloth_post_types"
            )
            raw_items = cur.fetchall()
        except Exception as e:
            abort(500)
        cur.close()
        items = []
        for item in raw_items:
            items.append({
                "uuid": item[0],
                "display_name": item[1],
                "slug": item[2]
            })
        return items

    def get_post_type(self, connection, post_type_id):
        cur = connection.cursor()
        raw_items = []
        try:
            cur.execute(
                sql.SQL(
                    """SELECT uuid, display_name, slug, tags_enabled, categories_enabled, archive_enabled 
                    FROM sloth_post_types WHERE uuid = %s"""
                ), [post_type_id]
            )
            raw_item = cur.fetchone()
        except Exception as e:
            abort(500)
        cur.close()

        return {
            "uuid": raw_item[0],
            "display_name": raw_item[1],
            "slug": raw_item[2],
            "tags_enabled": raw_item[3],
            "categories_enabled": raw_item[4],
            "archive_enabled": raw_item[5]
        }

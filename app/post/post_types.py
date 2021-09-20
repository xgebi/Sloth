import psycopg
from flask import abort
from psycopg2 import sql


class PostTypes:
    def __init__(self):
        pass

    # Placeholder for the future

    def get_post_type_list(self, connection: psycopg.Connection):
        with connection.cursor() as cur:
            raw_items = []
            try:
                cur.execute(
                    """SELECT uuid, slug, display_name, tags_enabled, categories_enabled, archive_enabled 
                            FROM sloth_post_types"""
                )
                raw_items = cur.fetchall()
            except psycopg.errors.DatabaseError as e:
                abort(500)
            cur.close()

            return [{
                "uuid": item[0],
                "slug": item[1],
                "display_name": item[2],
                "tags_enabled": item[3],
                "categories_enabled": item[4],
                "archive_enabled": item[5]
            } for item in raw_items]

    def get_post_type(self, connection, post_type_id):
        cur = connection.cursor()
        try:
            cur.execute(
                sql.SQL(
                    """SELECT uuid, display_name, slug, tags_enabled, categories_enabled, archive_enabled 
                    FROM sloth_post_types WHERE uuid = %s"""
                ), [post_type_id]
            )
            raw_item = cur.fetchone()
            cur.close()
            return {
                "uuid": raw_item[0],
                "display_name": raw_item[1],
                "slug": raw_item[2],
                "tags_enabled": raw_item[3],
                "categories_enabled": raw_item[4],
                "archive_enabled": raw_item[5]
            }
        except Exception as e:
            abort(500)
        cur.close()

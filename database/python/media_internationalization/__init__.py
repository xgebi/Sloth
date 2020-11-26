import psycopg2
from psycopg2 import sql, errors
import uuid


def transform(connection):
    cur = connection.cursor()
    try:
        cur.execute(
            sql.SQL("""SELECT uuid, file_path, alt, wp_id FROM sloth_media""")
        )
        media = cur.fetchall()

        for med in media:
            cur.execute(
                sql.SQL(
                    """INSERT INTO sloth_media_alts 
                    VALUES (%s, %s, (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language'), 
                    %s);"""
                ),
                [str(uuid.uuid4()), med[0],  med[2]]
            )
        connection.commit()
    except Exception as e:
        print(e)
        return False
    cur.close()
    return True

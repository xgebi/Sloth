import psycopg
import uuid


def transform(connection):
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid, file_path, alt, wp_id FROM sloth_media""")
            media = cur.fetchall()

            for med in media:
                cur.execute(
                        """INSERT INTO sloth_media_alts 
                        VALUES (%s, %s, (SELECT settings_value FROM sloth_settings WHERE settings_name = 'main_language'), 
                        %s);""",
                    (str(uuid.uuid4()), med[0],  med[2])
                )
            connection.commit()
    except psycopg.errors.DatabaseError as e:
        print(e)
        return False
    return True

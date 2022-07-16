import uuid


def transform(connection):
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid FROM sloth_post_types""")
            post_types = [pt[0] for pt in cur.fetchall()]

            for pt in post_types:
                cur.execute(
                    """INSERT INTO sloth_post_formats (uuid, slug, display_name, post_type, deletable) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (str(uuid.uuid4()), "", "None", pt, False))
            connection.commit()
    except Exception as e:
        print(e)
        return False
    return True

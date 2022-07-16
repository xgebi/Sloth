import uuid


def transform(connection):
    try:
        with connection.cursor() as cur:
            cur.execute("""SELECT uuid, excerpt, content  FROM sloth_posts""")

            to_be_sections = [{
                "uuid": section[0],
                "excerpt": section[1],
                "content": section[2]
            } for section in cur.fetchall()]

            for section in to_be_sections:
                cur.execute(
                    """INSERT INTO sloth_post_sections (uuid, post, content, section_type, position) 
                    VALUES (%s, %s, %s, %s, %s), (%s, %s, %s, %s, %s)""",
                    (str(uuid.uuid4()), section["uuid"], section["excerpt"], "text", 0,
                     str(uuid.uuid4()), section["uuid"], section["content"], "text", 1))
            connection.commit()
    except Exception as e:
        print(e)
        return False

    return True

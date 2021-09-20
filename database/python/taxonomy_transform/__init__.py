import psycopg
import uuid


def transform(connection: psycopg.Connection):
    with connection.cursor() as cur:
        try:
            cur.execute("""SELECT uuid, categories, tags FROM sloth_posts""")
            posts = cur.fetchall()

            for post in posts:
                for category in post[1]:
                    cur.execute("""INSERT INTO sloth_post_taxonomies VALUES (%s, %s, %s)""",
                                (str(uuid.uuid4()), post[0], category))
                for tag in post[2]:
                    cur.execute("""INSERT INTO sloth_post_taxonomies VALUES (%s, %s, %s)""",
                                (str(uuid.uuid4()), post[0], tag))
            connection.commit()
        except Exception as e:
            print(e)
            return False
        cur.close()
        return True
    return False

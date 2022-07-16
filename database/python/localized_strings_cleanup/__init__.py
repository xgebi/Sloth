import psycopg


def transform(connection: psycopg.Connection):
    with connection.cursor() as cur:
        try:
            cur.execute("""SELECT name, standalone FROM sloth_localizable_strings;""")
            localizable = cur.fetchall()
            cur.execute("""SELECT uuid FROM sloth_post_types;""")
            post_types = [id[0] for id in cur.fetchall()]
            cur.execute("""SELECT uuid FROM sloth_language_settings""")
            languages = cur.fetchall()
            for item in localizable:
                cur.execute("""
                    SELECT uuid, name, content, lang, post_type 
                    FROM sloth_localized_strings WHERE name = %s""",
                            (item[0],))
                results = cur.fetchall()
                final_item = {}
                for res in results:
                    if res[3] not in final_item:
                        final_item[res[3]] = {
                            "uuid": res[0],
                            "name": res[1],
                            "content": res[2],
                            "lang": res[3],
                            "post_type": res[4],
                        }
                    elif len(res[2]) > 0:
                        final_item[res[3]]["content"] = res[2]
                for key in final_item.keys():
                    cur.execute("""DELETE FROM sloth_localized_strings WHERE name = %s AND lang = %s AND uuid <> %s""",
                                (final_item[key]["name"], final_item[key]["lang"], final_item[key]["uuid"]))
                    cur.execute("""UPDATE sloth_localized_strings SET content = %s WHERE uuid = %s""",
                                (final_item[key]["content"], final_item[key]["uuid"]))
            connection.commit()
        except Exception as e:
            print(e)
            return False
        cur.close()
        return True
    return False
